"""Metrics + tracing middleware for Celestra Core."""

from __future__ import annotations

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from monitoring.metrics import get_metrics
from monitoring.tracing import clear_trace, start_trace, trace_headers
from shared.logging.context import bind_context


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    - Correlates trace_id with request_id (or preserves explicit X-Trace-ID)
    - Records Prometheus request metrics
    - Tracks in-flight gauge
    """

    SKIP_PATHS = {"/metrics", "/health", "/ready", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = getattr(request.state, "request_id", None) or request.headers.get(
            "X-Request-ID"
        )
        explicit_trace = request.headers.get("X-Trace-ID")
        # Policy: primary correlation is request_id; trace_id defaults to it
        # unless the client explicitly sends X-Trace-ID.
        trace_seed = explicit_trace or request_id
        trace_id, span_id = start_trace(trace_id=trace_seed)
        if request_id:
            try:
                bind_context(request_id=request_id, trace_id=trace_id, span_id=span_id)
            except Exception:
                pass
        metrics = get_metrics()
        metrics.http_requests_in_progress.inc()
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            for key, value in trace_headers().items():
                response.headers[key] = value
            if request_id and "X-Request-ID" not in response.headers:
                response.headers["X-Request-ID"] = request_id
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
