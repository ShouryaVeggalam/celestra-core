"""Notification domain types."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from shared.utils.dates import utcnow
from shared.utils.ids import new_uuid


class NotificationChannel(str, Enum):
    EMAIL = "email"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(new_uuid()))
    channel: NotificationChannel
    recipient: str
    subject: str | None = None
    body: str
    payload: dict[str, Any] = Field(default_factory=dict)
    status: NotificationStatus = NotificationStatus.PENDING
    error: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    sent_at: datetime | None = None
    user_id: str | None = None


class SendNotificationRequest(BaseModel):
    channel: NotificationChannel | Literal["email", "webhook", "in_app"]
    recipient: str
    subject: str | None = None
    body: str
    payload: dict[str, Any] = Field(default_factory=dict)
    user_id: str | None = None
