"""In-app notification inbox."""

from __future__ import annotations

from notifications.base import NotificationSender
from notifications.types import Notification, NotificationStatus
from shared.utils.dates import utcnow


class InAppInbox:
    def __init__(self) -> None:
        self._items: dict[str, list[Notification]] = {}

    def add(self, notification: Notification) -> None:
        key = notification.user_id or notification.recipient
        self._items.setdefault(key, []).append(notification.model_copy(deep=True))

    def list_for(self, user_key: str, *, limit: int = 50) -> list[Notification]:
        items = self._items.get(user_key, [])
        return [i.model_copy(deep=True) for i in reversed(items[-limit:])]

    def clear(self, user_key: str) -> None:
        self._items.pop(user_key, None)


class InAppSender(NotificationSender):
    channel = "in_app"

    def __init__(self, inbox: InAppInbox | None = None) -> None:
        self.inbox = inbox or InAppInbox()

    async def send(self, notification: Notification) -> Notification:
        notification.status = NotificationStatus.SENT
        notification.sent_at = utcnow()
        self.inbox.add(notification)
        return notification
