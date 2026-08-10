"""Object storage types."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from shared.utils.dates import utcnow


class ObjectInfo(BaseModel):
    key: str
    bucket: str = "default"
    size: int = 0
    content_type: str = "application/octet-stream"
    etag: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    url: str | None = None


class StoredObject(BaseModel):
    info: ObjectInfo
    data: bytes
