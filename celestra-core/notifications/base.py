"""Notification channel interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from notifications.types import Notification


class NotificationSender(ABC):
    channel: str

    @abstractmethod
    async def send(self, notification: Notification) -> Notification: ...
