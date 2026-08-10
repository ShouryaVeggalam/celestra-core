"""Knowledge / RAG domain types."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from shared.utils.dates import utcnow
from shared.utils.ids import new_uuid


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(new_uuid()))
    knowledge_base_id: str
    title: str
    source: str | None = None  # storage key or URI
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class Chunk(BaseModel):
    id: str = Field(default_factory=lambda: str(new_uuid()))
    document_id: str
    knowledge_base_id: str
    index: int
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeBase(BaseModel):
    id: str = Field(default_factory=lambda: str(new_uuid()))
    name: str
    description: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    document_count: int = 0


class IngestTextRequest(BaseModel):
    knowledge_base: str  # name or id
    title: str
    content: str
    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    knowledge_base: str
    question: str
    top_k: int = Field(default=4, ge=1, le=20)
    model: str | None = None


class QueryResponse(BaseModel):
    answer: str
    knowledge_base: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    model: str | None = None
    provider: str | None = None
