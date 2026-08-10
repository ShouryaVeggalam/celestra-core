"""Knowledge / RAG facade — ingest documents and answer grounded questions."""

from __future__ import annotations

from ai.schemas import CompleteRequest, EmbedRequest
from ai.service import AIService
from knowledge.chunking import chunk_text
from knowledge.store import KnowledgeStore
from knowledge.types import (
    Chunk,
    Document,
    IngestTextRequest,
    KnowledgeBase,
    QueryRequest,
    QueryResponse,
)
from memory.types import VectorRecord
from memory.vector import InMemoryVectorStore
from providers.types import Message, Role
from shared.exceptions.base import NotFoundError
from shared.logging.setup import get_logger
from storage.service import StorageService

logger = get_logger(__name__)


class KnowledgeService:
    def __init__(
        self,
        *,
        ai: AIService,
        store: KnowledgeStore | None = None,
        vectors: InMemoryVectorStore | None = None,
        storage: StorageService | None = None,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ) -> None:
        self.ai = ai
        self.store = store or KnowledgeStore()
        self.vectors = vectors or InMemoryVectorStore()
        self.storage = storage
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_knowledge_base(self, name: str, description: str = "") -> KnowledgeBase:
        return self.store.create_base(name, description)

    def list_knowledge_bases(self) -> list[KnowledgeBase]:
        return self.store.list_bases()

    def get_knowledge_base(self, name_or_id: str) -> KnowledgeBase:
        return self.store.get_base(name_or_id)

    async def ingest_text(self, request: IngestTextRequest) -> Document:
        kb = self._ensure_base(request.knowledge_base)
        document = Document(
            knowledge_base_id=kb.id,
            title=request.title,
            source=request.source,
            content=request.content,
            metadata=request.metadata,
        )
        self.store.add_document(document)

        # Optionally persist raw content to object storage
        if self.storage is not None:
            key = f"knowledge/{kb.id}/{document.id}.txt"
            await self.storage.upload(
                key,
                request.content.encode("utf-8"),
                content_type="text/plain",
                metadata={"title": request.title, "kb": kb.name},
            )
            document.source = document.source or key

        pieces = chunk_text(
            request.content,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap,
        )
        records: list[VectorRecord] = []
        for index, text in enumerate(pieces):
            chunk = Chunk(
                document_id=document.id,
                knowledge_base_id=kb.id,
                index=index,
                text=text,
                metadata={"title": document.title, **request.metadata},
            )
            embedded = await self.ai.embed(EmbedRequest(input=text))
            records.append(
                VectorRecord(
                    id=chunk.id,
                    text=chunk.text,
                    embedding=embedded.embeddings[0],
                    metadata={
                        "knowledge_base_id": kb.id,
                        "document_id": document.id,
                        "chunk_index": index,
                        "title": document.title,
                    },
                )
            )
        await self.vectors.upsert(records)
        logger.info(
            "knowledge_ingested",
            knowledge_base=kb.name,
            document_id=document.id,
            chunks=len(records),
        )
        return document

    async def query(self, request: QueryRequest) -> QueryResponse:
        kb = self.store.get_base(request.knowledge_base)
        embedded = await self.ai.embed(EmbedRequest(input=request.question))
        hits = await self.vectors.search(embedded.embeddings[0], top_k=request.top_k * 3)
        # Filter to this knowledge base
        scoped = [h for h in hits if h.metadata.get("knowledge_base_id") == kb.id][: request.top_k]
        if not scoped:
            return QueryResponse(
                answer="I could not find relevant information in this knowledge base.",
                knowledge_base=kb.name,
                sources=[],
            )

        context = "\n\n".join(
            f"[{i+1}] (doc={h.metadata.get('title')}) {h.text}" for i, h in enumerate(scoped)
        )
        completion = await self.ai.complete(
            CompleteRequest(
                messages=[
                    Message(
                        role=Role.SYSTEM,
                        content=(
                            "You are Celestra Knowledge. Answer using only the provided context. "
                            "If the context is insufficient, say so."
                        ),
                    ),
                    Message(
                        role=Role.USER,
                        content=f"Context:\n{context}\n\nQuestion: {request.question}",
                    ),
                ],
                model=request.model,
            )
        )
        sources = [
            {
                "chunk_id": h.id,
                "score": h.score,
                "title": h.metadata.get("title"),
                "document_id": h.metadata.get("document_id"),
                "text": h.text[:240],
            }
            for h in scoped
        ]
        return QueryResponse(
            answer=completion.content,
            knowledge_base=kb.name,
            sources=sources,
            model=completion.model,
            provider=completion.provider,
        )

    def list_documents(self, knowledge_base: str) -> list[Document]:
        kb = self.store.get_base(knowledge_base)
        return self.store.list_documents(kb.id)

    def _ensure_base(self, name_or_id: str) -> KnowledgeBase:
        try:
            return self.store.get_base(name_or_id)
        except NotFoundError:
            return self.store.create_base(name_or_id)
