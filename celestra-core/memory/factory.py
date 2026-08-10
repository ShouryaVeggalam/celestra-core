"""Memory backend factory — in-memory / Redis / Postgres."""

from __future__ import annotations

from config.settings import Settings
from database.session import async_session_factory
from memory.base import ConversationStore, VectorStore
from memory.buffer import InMemoryConversationStore
from memory.postgres_vector import PostgresVectorStore
from memory.redis_store import RedisConversationStore
from memory.vector import InMemoryVectorStore
from shared.logging.setup import get_logger
from shared.redis.client import RedisClient

logger = get_logger(__name__)


def build_conversation_store(settings: Settings, redis: RedisClient | None) -> ConversationStore:
    backend = settings.memory_conversation_backend
    if backend == "redis":
        if redis is None:
            logger.warning("memory_conversation_redis_unavailable_fallback_memory")
            return InMemoryConversationStore()
        return RedisConversationStore(redis, ttl_seconds=settings.memory_conversation_ttl_seconds)
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
