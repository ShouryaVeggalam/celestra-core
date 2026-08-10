"""Redis client lifecycle — shared connection pool."""

from __future__ import annotations

from typing import Optional

import redis.asyncio as aioredis

from config.settings import Settings, get_settings

_client: Optional["RedisClient"] = None


class RedisClient:
    def __init__(self, client: aioredis.Redis, prefix: str = "celestra:") -> None:
        self._client = client
        self.prefix = prefix

    def key(self, name: str) -> str:
        if name.startswith(self.prefix):
            return name
        return f"{self.prefix}{name}"

    @property
    def raw(self) -> aioredis.Redis:
        return self._client

    async def ping(self) -> bool:
        return bool(await self._client.ping())

    async def close(self) -> None:
        await self._client.aclose()


async def init_redis(settings: Settings | None = None) -> RedisClient:
    global _client
    cfg = settings or get_settings()
    raw = aioredis.from_url(cfg.redis_url, encoding="utf-8", decode_responses=True)
    _client = RedisClient(raw, prefix=cfg.redis_prefix)
    return _client


def get_redis() -> RedisClient:
    if _client is None:
        raise RuntimeError("Redis is not initialized. Call init_redis() during app startup.")
    return _client


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
