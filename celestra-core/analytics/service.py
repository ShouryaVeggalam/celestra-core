"""Analytics facade — product event tracking for Celestra apps."""

from __future__ import annotations

from analytics.store import AnalyticsStore
from analytics.types import AnalyticsEvent, EventCount, EventQuery, TrackEventRequest
from shared.exceptions.base import ValidationAppError
from shared.logging.setup import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self, store: AnalyticsStore | None = None) -> None:
        self.store = store or AnalyticsStore()

    def track(self, request: TrackEventRequest) -> AnalyticsEvent:
        name = request.name.strip()
        if not name:
            raise ValidationAppError("event name is required")
        event = AnalyticsEvent(
            name=name,
            account_id=request.account_id,
            user_id=request.user_id,
            properties=request.properties,
        )
        saved = self.store.append(event)
        logger.info(
            "analytics_event",
            event_name=saved.name,
            account_id=saved.account_id,
            user_id=saved.user_id,
        )
        try:
            from monitoring.metrics import get_metrics

            metrics = get_metrics()
            if hasattr(metrics, "analytics_events_total"):
                metrics.analytics_events_total.labels(event=saved.name).inc()
        except Exception:
            pass
        return saved

    def query(self, query: EventQuery) -> list[AnalyticsEvent]:
        return self.store.query(query)

    def counts(self, *, account_id: str | None = None) -> list[EventCount]:
        return self.store.counts(account_id=account_id)
