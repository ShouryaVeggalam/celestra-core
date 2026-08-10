"""Analytics HTTP API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from analytics.service import AnalyticsService
from analytics.types import AnalyticsEvent, EventCount, EventQuery, TrackEventRequest
from auth.dependencies import get_current_user
from auth.models import User
from core.container import Container, get_container
from shared.exceptions.base import ValidationAppError

router = APIRouter(prefix="/analytics", tags=["analytics"])


def provide_analytics_service(container: Annotated[Container, Depends(get_container)]) -> AnalyticsService:
    try:
        service = container.resolve("analytics_service")
    except KeyError as exc:
        raise ValidationAppError("Analytics service is not initialized") from exc
    assert isinstance(service, AnalyticsService)
    return service


@router.post("/track", response_model=AnalyticsEvent)
async def track(
    payload: TrackEventRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AnalyticsService, Depends(provide_analytics_service)],
) -> AnalyticsEvent:
    if payload.user_id is None:
        payload.user_id = str(user.id)
    return service.track(payload)


@router.post("/query", response_model=list[AnalyticsEvent])
async def query_events(
    payload: EventQuery,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[AnalyticsService, Depends(provide_analytics_service)],
) -> list[AnalyticsEvent]:
    return service.query(payload)


@router.get("/counts", response_model=list[EventCount])
async def event_counts(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[AnalyticsService, Depends(provide_analytics_service)],
    account_id: str | None = None,
) -> list[EventCount]:
    return service.counts(account_id=account_id)
