"""Build notification senders from settings."""

from __future__ import annotations

from config.settings import Settings, get_settings
from notifications.channels.email import LoggingEmailSender
from notifications.channels.inbox import InAppInbox, InAppSender
from notifications.channels.smtp import SMTPEmailSender
from notifications.channels.webhook import WebhookSender
from notifications.service import NotificationService
from shared.logging.setup import get_logger

logger = get_logger(__name__)


def build_notification_service(settings: Settings | None = None) -> NotificationService:
    cfg = settings or get_settings()
    inbox = InAppInbox()
    if cfg.smtp_host and cfg.smtp_from:
        email_sender: LoggingEmailSender | SMTPEmailSender = SMTPEmailSender(
            host=cfg.smtp_host,
            port=cfg.smtp_port,
            username=cfg.smtp_username,
            password=cfg.smtp_password,
            from_address=cfg.smtp_from,
            use_tls=cfg.smtp_use_tls,
        )
        logger.info("email_channel_smtp", host=cfg.smtp_host, port=cfg.smtp_port)
    else:
        email_sender = LoggingEmailSender()
        logger.info("email_channel_logging")
    senders = {
        "email": email_sender,
        "webhook": WebhookSender(),
        "in_app": InAppSender(inbox),
    }
    return NotificationService(senders, inbox=inbox)
