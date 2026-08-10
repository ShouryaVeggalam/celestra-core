"""FastAPI dependency providers."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings, get_settings
from core.container import Container, get_container
from database.session import get_async_session
from shared.redis.cache import CacheService
from shared.redis.client import RedisClient, get_redis


def provide_settings() -> Settings:
    return get_settings()


def provide_container() -> Container:
    return get_container()


def provide_redis() -> RedisClient:
    return get_redis()


def provide_cache() -> CacheService:
    container = get_container()
    if container.cache is None:
        raise RuntimeError("CacheService is not wired")
    return container.cache


async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session
