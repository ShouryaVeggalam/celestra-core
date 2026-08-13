"""Memory facade — conversation + semantic vector memory for product apps."""

from __future__ import annotations

from ai.schemas import EmbedRequest
from ai.service import AIService
from memory.conversation import ConversationMemory, normalize_application
from memory.types import (
    DEFAULT_APPLICATION,
    ConversationSession,
    MemoryMessage,
    VectorRecord,
    VectorSearchHit,
)
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

    async def start_session(
        self,
        *,
        session_id: str | None = None,
        user_id: str,
        application: str = DEFAULT_APPLICATION,
    ) -> ConversationSession:
        return await self.conversations.get_or_create(
            session_id,
            user_id=user_id,
            application=normalize_application(application),
        )

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        user_id: str,
        application: str = DEFAULT_APPLICATION,
    ) -> ConversationSession:
        """Append a message to an existing owned session (no auto-create)."""
        return await self.conversations.add(
            session_id,
            role,
            content,
            user_id=user_id,
            application=normalize_application(application),
        )

    async def get_messages(
        self,
        session_id: str,
        *,
        user_id: str,
        application: str = DEFAULT_APPLICATION,
    ) -> list[MemoryMessage]:
        return await self.conversations.window(
            session_id,
            user_id=user_id,
            application=normalize_application(application),
        )

    async def remember_text(
        self,
        text: str,
        *,
        metadata: dict | None = None,
        record_id: str | None = None,
    ) -> VectorRecord:
        # NOTE: Vector memory is NOT multi-user safe until recall filters by
        # user_id + application. Do not enable for production multi-tenant use.
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
        # NOTE: Unscoped across users/applications — unsuitable for multi-user prod.
        if self.ai is None:
            raise RuntimeError("AIService required for semantic memory")
        embedded = await self.ai.embed(EmbedRequest(input=query))
        return await self.vectors.search(embedded.embeddings[0], top_k=top_k)
