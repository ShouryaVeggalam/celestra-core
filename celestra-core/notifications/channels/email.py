"""Email channel — logs in foundation mode; swap for SES/SMTP later."""

from __future__ import annotations

from notifications.base import NotificationSender
from notifications.types import Notification, NotificationStatus
from shared.logging.setup import get_logger
from shared.utils.dates import utcnow

logger = get_logger(__name__)


class LoggingEmailSender(NotificationSender):
    """Development email sender that records instead of SMTP delivery."""

    channel = "email"

    def __init__(self) -> None:
        self.outbox: list[Notification] = []

    async def send(self, notification: Notification) -> Notification:
        notification.status = NotificationStatus.SENT
        notification.sent_at = utcnow()
        self.outbox.append(notification.model_copy(deep=True))
        logger.info(
            "email_notification_sent",
            recipient=notification.recipient,
            subject=notification.subject,
            notification_id=notification.id,
        )
        return notification
