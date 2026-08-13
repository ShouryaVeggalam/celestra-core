"""Memory backend factory — in-memory / Redis / Postgres."""

from __future__ import annotations

from config.settings import Settings
from database.session import async_session_factory
from memory.base import ConversationStore, VectorStore
from memory.buffer import InMemoryConversationStore
from memory.postgres_vector import PostgresVectorStore
from memory.redis_store import RedisConversationStore
from memory.vector import InMemoryVectorStore
from shared.exceptions.base import ConfigurationError
from shared.logging.setup import get_logger
from shared.redis.client import RedisClient

logger = get_logger(__name__)


def build_conversation_store(settings: Settings, redis: RedisClient | None) -> ConversationStore:
    """Build conversation store.

    When ``memory_conversation_backend=redis``, Redis MUST be available.
    There is no silent fallback to in-memory (avoids false durability).
    """
    backend = settings.memory_conversation_backend
    if backend == "redis":
        if redis is None:
            raise ConfigurationError(
                "CELESTRA_MEMORY_CONVERSATION_BACKEND=redis but Redis is not initialized",
                details={"backend": "redis"},
            )
        logger.info(
            "memory_conversation_backend_redis",
            ttl_seconds=settings.memory_conversation_ttl_seconds,
        )
        return RedisConversationStore(
            redis, ttl_seconds=settings.memory_conversation_ttl_seconds
        )
    logger.info("memory_conversation_backend_memory")
    return InMemoryConversationStore()


def build_vector_store(settings: Settings, *, namespace: str = "default") -> VectorStore:
    backend = settings.memory_vector_backend
    if backend == "postgres":
        try:
            return PostgresVectorStore(async_session_factory(), namespace=namespace)
        except Exception as exc:
            logger.warning("memory_vector_postgres_unavailable_fallback_memory", error=str(exc))
            return InMemoryVectorStore()
    return InMemoryVectorStore()
