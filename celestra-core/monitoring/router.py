"""Monitoring HTTP endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from auth.dependencies import require_permissions
from auth.models import User
from config.settings import Settings, get_settings
from monitoring.metrics import get_metrics
from monitoring.tracing import get_trace_id

router = APIRouter(tags=["monitoring"])


class MonitoringStatus(BaseModel):
    status: str
    app: str
    env: str
    trace_id: str | None
    metrics_enabled: bool


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    """Prometheus scrape endpoint (unauthenticated for scraper simplicity)."""
    body, content_type = get_metrics().render_prometheus()
    return Response(content=body, media_type=content_type)


@router.get("/monitoring/status", response_model=MonitoringStatus)
async def monitoring_status(
    settings: Settings = Depends(get_settings),
    _: User = Depends(require_permissions("monitoring:read")),
) -> MonitoringStatus:
    return MonitoringStatus(
        status="ok",
        app=settings.app_name,
        env=settings.env.value,
        trace_id=get_trace_id(),
        metrics_enabled=True,
    )
