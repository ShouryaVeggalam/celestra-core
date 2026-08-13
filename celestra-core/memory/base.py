"""Memory store interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

from memory.types import ConversationSession, MemoryMessage, VectorRecord, VectorSearchHit


class ConversationStore(ABC):
    @abstractmethod
    async def get(
        self, session_id: str, *, application: str = "default"
    ) -> ConversationSession | None: ...

    @abstractmethod
    async def save(self, session: ConversationSession) -> ConversationSession: ...

    @abstractmethod
    async def delete(self, session_id: str, *, application: str = "default") -> None: ...

    @abstractmethod
    async def append(
        self,
        session_id: str,
        messages: list[MemoryMessage],
        *,
        application: str = "default",
    ) -> ConversationSession: ...


class VectorStore(ABC):
    @abstractmethod
    async def upsert(self, records: list[VectorRecord]) -> None: ...

    @abstractmethod
    async def search(self, embedding: list[float], *, top_k: int = 5) -> list[VectorSearchHit]: ...

    @abstractmethod
    async def delete(self, record_id: str) -> None: ...
