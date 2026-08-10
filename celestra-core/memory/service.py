"""Memory facade — conversation + semantic vector memory for product apps."""

from __future__ import annotations

from ai.schemas import EmbedRequest
from ai.service import AIService
from memory.conversation import ConversationMemory
from memory.types import ConversationSession, MemoryMessage, VectorRecord, VectorSearchHit
from memory.vector import InMemoryVectorStore
from shared.utils.ids import new_uuid


class MemoryService:
    def __init__(
        self,
        *,
        conversations: ConversationMemory,
        vectors: InMemoryVectorStore,
        ai: AIService | None = None,
    ) -> None:
        self.conversations = conversations
        self.vectors = vectors
        self.ai = ai

    async def start_session(self, *, session_id: str | None = None, user_id: str | None = None) -> ConversationSession:
        return await self.conversations.get_or_create(session_id, user_id=user_id)

    async def add_message(self, session_id: str, role: str, content: str) -> ConversationSession:
        return await self.conversations.add(session_id, role, content)

    async def get_messages(self, session_id: str) -> list[MemoryMessage]:
        return await self.conversations.window(session_id)

    async def remember_text(
        self,
        text: str,
        *,
        metadata: dict | None = None,
        record_id: str | None = None,
    ) -> VectorRecord:
        if self.ai is None:
            raise RuntimeError("AIService required for semantic memory")
        embedded = await self.ai.embed(EmbedRequest(input=text))
        record = VectorRecord(
            id=record_id or str(new_uuid()),
            text=text,
            embedding=embedded.embeddings[0],
            metadata=metadata or {},
        )
        await self.vectors.upsert([record])
        return record

    async def recall(self, query: str, *, top_k: int = 5) -> list[VectorSearchHit]:
        if self.ai is None:
            raise RuntimeError("AIService required for semantic memory")
        embedded = await self.ai.embed(EmbedRequest(input=query))
        return await self.vectors.search(embedded.embeddings[0], top_k=top_k)
