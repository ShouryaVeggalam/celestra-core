"""In-process conversation store — default for tests and single-worker dev."""

from __future__ import annotations

from memory.base import ConversationStore
from memory.types import ConversationSession, MemoryMessage
from shared.exceptions.base import NotFoundError
from shared.utils.dates import utcnow


class InMemoryConversationStore(ConversationStore):
    def __init__(self) -> None:
        self._sessions: dict[str, ConversationSession] = {}

    async def get(self, session_id: str) -> ConversationSession | None:
        session = self._sessions.get(session_id)
        return session.model_copy(deep=True) if session else None

    async def save(self, session: ConversationSession) -> ConversationSession:
        session.updated_at = utcnow()
        self._sessions[session.id] = session.model_copy(deep=True)
        return session.model_copy(deep=True)

    async def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    async def append(self, session_id: str, messages: list[MemoryMessage]) -> ConversationSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise NotFoundError(f"Conversation session '{session_id}' not found")
        session.messages.extend(messages)
        session.updated_at = utcnow()
        self._sessions[session_id] = session
        return session.model_copy(deep=True)
