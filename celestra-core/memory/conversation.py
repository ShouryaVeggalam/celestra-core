"""Conversation memory helpers — windowing and formatting for agents/AI."""

from __future__ import annotations

from memory.base import ConversationStore
from memory.types import ConversationSession, MemoryMessage
from providers.types import Message, Role
from shared.utils.dates import utcnow
from shared.utils.ids import new_uuid


class ConversationMemory:
    """High-level conversation memory API over a ConversationStore."""

    def __init__(self, store: ConversationStore, *, window_size: int = 20) -> None:
        self.store = store
        self.window_size = window_size

    async def get_or_create(self, session_id: str | None = None, *, user_id: str | None = None) -> ConversationSession:
        sid = session_id or str(new_uuid())
        existing = await self.store.get(sid)
        if existing:
            return existing
        session = ConversationSession(id=sid, user_id=user_id)
        return await self.store.save(session)

    async def add(self, session_id: str, role: str, content: str, **metadata: object) -> ConversationSession:
        return await self.store.append(
            session_id,
            [MemoryMessage(role=role, content=content, metadata=dict(metadata))],  # type: ignore[arg-type]
        )

    async def window(self, session_id: str) -> list[MemoryMessage]:
        session = await self.store.get(session_id)
        if session is None:
            return []
        return session.messages[-self.window_size :]

    async def as_provider_messages(self, session_id: str) -> list[Message]:
        messages = await self.window(session_id)
        result: list[Message] = []
        for msg in messages:
            result.append(Message(role=Role(msg.role), content=msg.content))
        return result

    async def clear(self, session_id: str) -> None:
        await self.store.delete(session_id)

    async def touch(self, session: ConversationSession) -> ConversationSession:
        session.updated_at = utcnow()
        return await self.store.save(session)
