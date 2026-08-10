"""Metrics + tracing middleware for Celestra Core."""

from __future__ import annotations

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from monitoring.metrics import get_metrics
from monitoring.tracing import clear_trace, start_trace, trace_headers


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    - Ensures X-Trace-ID / X-Span-ID
    - Records Prometheus request metrics
    - Tracks in-flight gauge
    """

    SKIP_PATHS = {"/metrics", "/health", "/ready", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        incoming = request.headers.get("X-Trace-ID") or request.headers.get("X-Request-ID")
        trace_id, span_id = start_trace(trace_id=incoming)
        metrics = get_metrics()
        metrics.http_requests_in_progress.inc()
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            for key, value in trace_headers().items():
                response.headers[key] = value
            return response
        finally:
            duration = time.perf_counter() - started
            metrics.http_requests_in_progress.dec()
            if request.url.path not in self.SKIP_PATHS:
                metrics.observe_request(
                    method=request.method,
                    path=request.url.path,
                    status=status_code,
                    duration_seconds=duration,
                )
            clear_trace()
