"""Webhook notification channel."""

from __future__ import annotations

import httpx

from notifications.base import NotificationSender
from notifications.types import Notification, NotificationStatus
from shared.exceptions.base import ExternalServiceError
from shared.logging.setup import get_logger
from shared.utils.dates import utcnow

logger = get_logger(__name__)


class WebhookSender(NotificationSender):
    channel = "webhook"

    def __init__(self, *, timeout: float = 15.0) -> None:
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def send(self, notification: Notification) -> Notification:
        payload = {
            "id": notification.id,
            "subject": notification.subject,
            "body": notification.body,
            "payload": notification.payload,
            "created_at": notification.created_at.isoformat(),
        }
        try:
            response = await self._client.post(notification.recipient, json=payload)
            if response.status_code >= 400:
                raise ExternalServiceError(
                    f"Webhook failed: {response.status_code}",
                    details={"body": response.text[:300]},
                )
            notification.status = NotificationStatus.SENT
            notification.sent_at = utcnow()
            logger.info("webhook_notification_sent", url=notification.recipient, id=notification.id)
            return notification
        except Exception as exc:
            notification.status = NotificationStatus.FAILED
            notification.error = str(exc)
            logger.warning("webhook_notification_failed", error=str(exc), url=notification.recipient)
            raise
