"""
Monitoring module — metrics, tracing, and observability primitives.

Builds on Phase 1 structured logging. Product apps should emit metrics and
events through this module rather than inventing their own instrumentation.
"""

from monitoring.events import emit_event
from monitoring.metrics import MetricsRegistry, get_metrics, init_metrics
from monitoring.middleware import MonitoringMiddleware
from monitoring.router import router as monitoring_router
from monitoring.tracing import (
    clear_trace,
    get_span_id,
    get_trace_id,
    start_trace,
    trace_headers,
)

__all__ = [
    "MetricsRegistry",
    "MonitoringMiddleware",
    "clear_trace",
    "emit_event",
    "get_metrics",
    "get_span_id",
    "get_trace_id",
    "init_metrics",
    "monitoring_router",
    "start_trace",
    "trace_headers",
]
