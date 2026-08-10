"""Notifications HTTP API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from auth.models import User
from core.container import Container, get_container
from notifications.service import NotificationService
from notifications.types import Notification, SendNotificationRequest
from shared.exceptions.base import ValidationAppError

router = APIRouter(prefix="/notifications", tags=["notifications"])


def provide_notification_service(
    container: Annotated[Container, Depends(get_container)],
) -> NotificationService:
    try:
        service = container.resolve("notification_service")
    except KeyError as exc:
        raise ValidationAppError("Notification service is not initialized") from exc
    assert isinstance(service, NotificationService)
    return service


@router.post("/send", response_model=Notification)
async def send_notification(
    payload: SendNotificationRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[NotificationService, Depends(provide_notification_service)],
) -> Notification:
    if payload.user_id is None:
        payload.user_id = str(user.id)
    return await service.send(payload)


@router.get("/inbox", response_model=list[Notification])
async def inbox(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[NotificationService, Depends(provide_notification_service)],
) -> list[Notification]:
    return service.list_inbox(str(user.id))
