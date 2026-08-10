"""Redis-backed conversation store for multi-worker deployments."""

from __future__ import annotations

from memory.base import ConversationStore
from memory.types import ConversationSession, MemoryMessage
from shared.exceptions.base import NotFoundError
from shared.redis.client import RedisClient
from shared.utils.dates import utcnow


class RedisConversationStore(ConversationStore):
    def __init__(self, redis: RedisClient, *, ttl_seconds: int = 60 * 60 * 24 * 7) -> None:
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    def _key(self, session_id: str) -> str:
        return self.redis.key(f"memory:conversation:{session_id}")

    async def get(self, session_id: str) -> ConversationSession | None:
        raw = await self.redis.raw.get(self._key(session_id))
        if raw is None:
            return None
        return ConversationSession.model_validate_json(raw)

    async def save(self, session: ConversationSession) -> ConversationSession:
        session.updated_at = utcnow()
        await self.redis.raw.set(
            self._key(session.id),
            session.model_dump_json(),
            ex=self.ttl_seconds,
        )
        return session.model_copy(deep=True)

    async def delete(self, session_id: str) -> None:
        await self.redis.raw.delete(self._key(session_id))

    async def append(self, session_id: str, messages: list[MemoryMessage]) -> ConversationSession:
        session = await self.get(session_id)
        if session is None:
            raise NotFoundError(f"Conversation session '{session_id}' not found")
        session.messages.extend(messages)
        return await self.save(session)
