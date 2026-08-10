"""Notification dispatcher facade."""

from __future__ import annotations

from notifications.base import NotificationSender
from notifications.channels.inbox import InAppInbox
from notifications.types import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    SendNotificationRequest,
)
from shared.exceptions.base import ValidationAppError
from shared.logging.setup import get_logger

logger = get_logger(__name__)


class NotificationService:
    def __init__(
        self,
        senders: dict[str, NotificationSender],
        *,
        inbox: InAppInbox | None = None,
    ) -> None:
        self.senders = senders
        self.inbox = inbox
        self.history: list[Notification] = []

    async def send(self, request: SendNotificationRequest) -> Notification:
        channel = (
            request.channel.value
            if isinstance(request.channel, NotificationChannel)
            else str(request.channel)
        )
        sender = self.senders.get(channel)
        if sender is None:
            raise ValidationAppError(
                f"Notification channel '{channel}' is not configured",
                details={"available": sorted(self.senders)},
            )
        notification = Notification(
            channel=NotificationChannel(channel),
            recipient=request.recipient,
            subject=request.subject,
            body=request.body,
            payload=request.payload,
            user_id=request.user_id,
        )
        try:
            result = await sender.send(notification)
        except Exception as exc:
            notification.status = NotificationStatus.FAILED
            notification.error = str(exc)
            self.history.append(notification.model_copy(deep=True))
            raise
        self.history.append(result.model_copy(deep=True))
        logger.info("notification_dispatched", channel=channel, id=result.id, status=result.status.value)
        return result

    def list_inbox(self, user_key: str) -> list[Notification]:
        if self.inbox is None:
            return []
        return self.inbox.list_for(user_key)
