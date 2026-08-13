"""Redis-backed conversation store for multi-worker deployments.

Append uses a Lua script so concurrent writers cannot silently overwrite each other.
TTL is refreshed on every successful save/append (default 7 days via settings).
"""

from __future__ import annotations

import json

from memory.base import ConversationStore
from memory.types import DEFAULT_APPLICATION, ConversationSession, MemoryMessage
from shared.exceptions.base import ConflictError, NotFoundError
from shared.redis.client import RedisClient
from shared.utils.dates import utcnow

# Atomic get → append messages → set with TTL. Returns updated JSON or false if missing.
_APPEND_LUA = """
local key = KEYS[1]
local raw = redis.call('GET', key)
if not raw then
  return false
end
local session = cjson.decode(raw)
local incoming = cjson.decode(ARGV[1])
for i = 1, #incoming do
  table.insert(session['messages'], incoming[i])
end
session['updated_at'] = ARGV[2]
local encoded = cjson.encode(session)
local ttl = tonumber(ARGV[3])
if ttl and ttl > 0 then
  redis.call('SET', key, encoded, 'EX', ttl)
else
  redis.call('SET', key, encoded)
end
return encoded
"""


class RedisConversationStore(ConversationStore):
    def __init__(self, redis: RedisClient, *, ttl_seconds: int = 60 * 60 * 24 * 7) -> None:
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    def _key(self, session_id: str, application: str = DEFAULT_APPLICATION) -> str:
        app = application or DEFAULT_APPLICATION
        return self.redis.key(f"memory:{app}:conversation:{session_id}")

    def _legacy_key(self, session_id: str) -> str:
        """Pre-hardening key layout (application=default only)."""
        return self.redis.key(f"memory:conversation:{session_id}")

    async def get(
        self, session_id: str, *, application: str = DEFAULT_APPLICATION
    ) -> ConversationSession | None:
        app = application or DEFAULT_APPLICATION
        raw = await self.redis.raw.get(self._key(session_id, app))
        if raw is None and app == DEFAULT_APPLICATION:
            raw = await self.redis.raw.get(self._legacy_key(session_id))
        if raw is None:
            return None
        session = ConversationSession.model_validate_json(raw)
        if not session.application:
            session.application = DEFAULT_APPLICATION
        return session

    async def save(self, session: ConversationSession) -> ConversationSession:
        session.updated_at = utcnow()
        session.application = session.application or DEFAULT_APPLICATION
        await self.redis.raw.set(
            self._key(session.id, session.application),
            session.model_dump_json(),
            ex=self.ttl_seconds,
        )
        return session.model_copy(deep=True)

    async def delete(
        self, session_id: str, *, application: str = DEFAULT_APPLICATION
    ) -> None:
        app = application or DEFAULT_APPLICATION
        await self.redis.raw.delete(self._key(session_id, app))
        if app == DEFAULT_APPLICATION:
            await self.redis.raw.delete(self._legacy_key(session_id))

    async def append(
        self,
        session_id: str,
        messages: list[MemoryMessage],
        *,
        application: str = DEFAULT_APPLICATION,
    ) -> ConversationSession:
        app = application or DEFAULT_APPLICATION
        key = self._key(session_id, app)
        # Prefer new key; if missing and default app, try legacy once then rewrite to new key.
        exists = await self.redis.raw.get(key)
        if exists is None and app == DEFAULT_APPLICATION:
            legacy = await self.redis.raw.get(self._legacy_key(session_id))
            if legacy is not None:
                await self.redis.raw.set(key, legacy, ex=self.ttl_seconds)

        payload = json.dumps([m.model_dump(mode="json") for m in messages])
        updated_at = utcnow().isoformat()
        result = await self.redis.raw.eval(
            _APPEND_LUA,
            1,
            key,
            payload,
            updated_at,
            str(self.ttl_seconds),
        )
        if result is None or result is False:
            raise NotFoundError(f"Conversation session '{session_id}' not found")
        if isinstance(result, bytes):
            result = result.decode("utf-8")
        try:
            return ConversationSession.model_validate_json(result)
        except Exception as exc:  # noqa: BLE001
            raise ConflictError(
                "Failed to decode conversation after atomic append",
                details={"session_id": session_id},
            ) from exc
