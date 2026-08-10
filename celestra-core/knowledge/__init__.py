"""
Knowledge module — document ingestion and RAG for Celestra apps.

Product apps use KnowledgeService instead of building their own RAG stacks.
"""

from __future__ import annotations

from typing import Any

from knowledge.service import KnowledgeService
from knowledge.types import Document, IngestTextRequest, KnowledgeBase, QueryRequest, QueryResponse

__all__ = [
    "Document",
    "IngestTextRequest",
    "KnowledgeBase",
    "KnowledgeService",
    "QueryRequest",
    "QueryResponse",
    "knowledge_router",
]


def __getattr__(name: str) -> Any:
    if name == "knowledge_router":
        from knowledge.http import router as knowledge_router

        return knowledge_router
    raise AttributeError(name)
