"""Analytics event types."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from shared.utils.dates import utcnow
from shared.utils.ids import new_uuid


class AnalyticsEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(new_uuid()))
    name: str
    account_id: str | None = None
    user_id: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utcnow)


class TrackEventRequest(BaseModel):
    name: str
    account_id: str | None = None
    user_id: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class EventQuery(BaseModel):
    name: str | None = None
    account_id: str | None = None
    user_id: str | None = None
    limit: int = Field(default=100, ge=1, le=1000)


class EventCount(BaseModel):
    name: str
    count: int
