"""Database session / engine lifecycle."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.settings import Settings, get_settings

_async_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
_sync_engine: Optional[Engine] = None


def init_async_engine(settings: Settings | None = None) -> AsyncEngine:
    global _async_engine, _async_session_factory
    if _async_engine is not None:
        return _async_engine

    cfg = settings or get_settings()
    _async_engine = create_async_engine(
        cfg.database_url,
        pool_size=cfg.db_pool_size,
        max_overflow=cfg.db_max_overflow,
        echo=cfg.db_echo,
        pool_pre_ping=True,
    )
    _async_session_factory = async_sessionmaker(
        bind=_async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    return _async_engine


def async_session_factory() -> async_sessionmaker[AsyncSession]:
    if _async_session_factory is None:
        init_async_engine()
    assert _async_session_factory is not None
    return _async_session_factory


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    factory = async_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_sync_engine(settings: Settings | None = None) -> Engine:
    global _sync_engine
    if _sync_engine is not None:
        return _sync_engine

    cfg = settings or get_settings()
    _sync_engine = create_engine(
        cfg.database_url_sync,
        pool_size=cfg.db_pool_size,
        max_overflow=cfg.db_max_overflow,
        echo=cfg.db_echo,
        pool_pre_ping=True,
    )
    return _sync_engine


async def dispose_async_engine() -> None:
    global _async_engine, _async_session_factory
    if _async_engine is not None:
        await _async_engine.dispose()
    _async_engine = None
    _async_session_factory = None


def dispose_sync_engine() -> None:
    global _sync_engine
    if _sync_engine is not None:
        _sync_engine.dispose()
    _sync_engine = None
