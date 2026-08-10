"""Reusable cache layer built on Redis."""

from __future__ import annotations

import json
from typing import Any, Callable

from shared.redis.client import RedisClient


class CacheService:
    def __init__(
        self,
        redis: RedisClient,
        *,
        default_ttl: int = 300,
        serializer: Callable[[Any], str] | None = None,
        deserializer: Callable[[str], Any] | None = None,
    ) -> None:
        self._redis = redis
        self.default_ttl = default_ttl
        self._serialize = serializer or (lambda value: json.dumps(value, default=str))
        self._deserialize = deserializer or json.loads

    async def get(self, key: str) -> Any | None:
        raw = await self._redis.raw.get(self._redis.key(f"cache:{key}"))
        if raw is None:
            return None
        return self._deserialize(raw)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        await self._redis.raw.set(
            self._redis.key(f"cache:{key}"),
            self._serialize(value),
            ex=ttl if ttl is not None else self.default_ttl,
        )

    async def delete(self, key: str) -> None:
        await self._redis.raw.delete(self._redis.key(f"cache:{key}"))

    async def exists(self, key: str) -> bool:
        return bool(await self._redis.raw.exists(self._redis.key(f"cache:{key}")))

    async def get_or_set(self, key: str, factory: Callable[[], Any], ttl: int | None = None) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = factory()
        if hasattr(value, "__await__"):
            value = await value  # type: ignore[misc]
        await self.set(key, value, ttl=ttl)
        return value
