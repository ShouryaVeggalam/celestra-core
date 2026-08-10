"""
Analytics module — product analytics events for Celestra apps.
"""

from __future__ import annotations

from typing import Any

from analytics.service import AnalyticsService
from analytics.types import AnalyticsEvent, EventQuery, TrackEventRequest

__all__ = [
    "AnalyticsEvent",
    "AnalyticsService",
    "EventQuery",
    "TrackEventRequest",
    "analytics_router",
]


def __getattr__(name: str) -> Any:
    if name == "analytics_router":
        from analytics.http import router as analytics_router

        return analytics_router
    raise AttributeError(name)
