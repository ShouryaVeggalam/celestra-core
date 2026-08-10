"""
Notifications module — email, webhook, and in-app dispatch.

Product apps send through NotificationService, not ad-hoc SMTP/webhooks.
"""

from __future__ import annotations

from typing import Any

from notifications.service import NotificationService
from notifications.types import Notification, NotificationChannel, SendNotificationRequest

__all__ = [
    "Notification",
    "NotificationChannel",
    "NotificationService",
    "SendNotificationRequest",
    "notifications_router",
]


def __getattr__(name: str) -> Any:
    if name == "notifications_router":
        from notifications.http import router as notifications_router

        return notifications_router
    raise AttributeError(name)
