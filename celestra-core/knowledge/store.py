"""In-memory knowledge base / document registry."""

from __future__ import annotations

from knowledge.types import Document, KnowledgeBase
from shared.exceptions.base import ConflictError, NotFoundError


class KnowledgeStore:
    def __init__(self) -> None:
        self._bases: dict[str, KnowledgeBase] = {}  # id -> kb
        self._by_name: dict[str, str] = {}  # name -> id
        self._documents: dict[str, Document] = {}

    def create_base(self, name: str, description: str = "") -> KnowledgeBase:
        if name in self._by_name:
            raise ConflictError(f"Knowledge base '{name}' already exists")
        kb = KnowledgeBase(name=name, description=description)
        self._bases[kb.id] = kb
        self._by_name[name] = kb.id
        return kb.model_copy(deep=True)

    def get_base(self, name_or_id: str) -> KnowledgeBase:
        kb_id = self._by_name.get(name_or_id, name_or_id)
        kb = self._bases.get(kb_id)
        if kb is None:
            raise NotFoundError(f"Knowledge base '{name_or_id}' not found")
        return kb.model_copy(deep=True)

    def list_bases(self) -> list[KnowledgeBase]:
        return sorted((b.model_copy(deep=True) for b in self._bases.values()), key=lambda b: b.name)

    def add_document(self, document: Document) -> Document:
        self._documents[document.id] = document.model_copy(deep=True)
        kb = self._bases[document.knowledge_base_id]
        kb.document_count += 1
        return document.model_copy(deep=True)

    def list_documents(self, knowledge_base_id: str) -> list[Document]:
        docs = [d for d in self._documents.values() if d.knowledge_base_id == knowledge_base_id]
        return sorted((d.model_copy(deep=True) for d in docs), key=lambda d: d.created_at)
