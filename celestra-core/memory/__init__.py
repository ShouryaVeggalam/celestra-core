"""
Memory module — conversation and semantic memory for Celestra apps.

Product apps must not invent their own chat history / RAG stores; import this.
"""

from memory.conversation import ConversationMemory
from memory.service import MemoryService
from memory.types import ConversationSession, MemoryMessage, VectorRecord, VectorSearchHit
from memory.vector import InMemoryVectorStore, cosine_similarity

__all__ = [
    "ConversationMemory",
    "ConversationSession",
    "InMemoryVectorStore",
    "MemoryMessage",
    "MemoryService",
    "VectorRecord",
    "VectorSearchHit",
    "cosine_similarity",
]
