"""Memory domain types."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from shared.utils.dates import utcnow
from shared.utils.ids import new_uuid

DEFAULT_APPLICATION = "default"


class MemoryMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class ConversationSession(BaseModel):
    id: str
    user_id: str | None = None
    # Product namespace (revenue | hiring | finance | default). Additive for compatibility.
    application: str = DEFAULT_APPLICATION
    messages: list[MemoryMessage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class VectorRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(new_uuid()))
    text: str
    embedding: list[float] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class VectorSearchHit(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)
