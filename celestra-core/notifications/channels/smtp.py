"""SMTP email sender — production delivery when SMTP is configured."""

from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage

from notifications.base import NotificationSender
from notifications.types import Notification, NotificationStatus
from shared.logging.setup import get_logger
from shared.utils.dates import utcnow

logger = get_logger(__name__)


class SMTPEmailSender(NotificationSender):
    channel = "email"

    def __init__(
        self,
        *,
        host: str,
        port: int = 587,
        username: str | None = None,
        password: str | None = None,
        from_address: str,
        use_tls: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.use_tls = use_tls

    def _deliver(self, notification: Notification) -> None:
        msg = EmailMessage()
        msg["Subject"] = notification.subject or "(no subject)"
        msg["From"] = self.from_address
        msg["To"] = notification.recipient
        body = notification.body or ""
        msg.set_content(body)

        with smtplib.SMTP(self.host, self.port, timeout=30) as smtp:
            if self.use_tls:
                smtp.starttls()
            if self.username and self.password:
                smtp.login(self.username, self.password)
            smtp.send_message(msg)

    async def send(self, notification: Notification) -> Notification:
        try:
            await asyncio.to_thread(self._deliver, notification)
            notification.status = NotificationStatus.SENT
            notification.sent_at = utcnow()
            logger.info(
                "smtp_email_sent",
                recipient=notification.recipient,
                subject=notification.subject,
                notification_id=notification.id,
            )
        except Exception as exc:
            notification.status = NotificationStatus.FAILED
            logger.error(
                "smtp_email_failed",
                recipient=notification.recipient,
                error=str(exc),
                notification_id=notification.id,
            )
            raise
        return notification
