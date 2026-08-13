"""In-process conversation store — default for tests and single-worker dev."""

from __future__ import annotations

import asyncio

from memory.base import ConversationStore
from memory.types import DEFAULT_APPLICATION, ConversationSession, MemoryMessage
from shared.exceptions.base import NotFoundError
from shared.utils.dates import utcnow


class InMemoryConversationStore(ConversationStore):
    def __init__(self) -> None:
        self._sessions: dict[tuple[str, str], ConversationSession] = {}
        self._lock = asyncio.Lock()

    def _key(self, session_id: str, application: str) -> tuple[str, str]:
        return ((application or DEFAULT_APPLICATION), session_id)

    async def get(
        self, session_id: str, *, application: str = DEFAULT_APPLICATION
    ) -> ConversationSession | None:
        session = self._sessions.get(self._key(session_id, application))
        return session.model_copy(deep=True) if session else None

    async def save(self, session: ConversationSession) -> ConversationSession:
        session.updated_at = utcnow()
        app = session.application or DEFAULT_APPLICATION
        session.application = app
        self._sessions[self._key(session.id, app)] = session.model_copy(deep=True)
        return session.model_copy(deep=True)

    async def delete(
        self, session_id: str, *, application: str = DEFAULT_APPLICATION
    ) -> None:
        self._sessions.pop(self._key(session_id, application), None)

    async def append(
        self,
        session_id: str,
        messages: list[MemoryMessage],
        *,
        application: str = DEFAULT_APPLICATION,
    ) -> ConversationSession:
        async with self._lock:
            key = self._key(session_id, application)
            session = self._sessions.get(key)
            if session is None:
                raise NotFoundError(f"Conversation session '{session_id}' not found")
            session.messages.extend(messages)
            session.updated_at = utcnow()
            self._sessions[key] = session
            return session.model_copy(deep=True)
