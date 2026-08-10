"""Performance logging middleware — records slow requests."""

from __future__ import annotations

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from shared.logging.setup import get_logger

logger = get_logger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, *, enabled: bool = True, slow_threshold_ms: float = 1000.0) -> None:
        super().__init__(app)
        self.enabled = enabled
        self.slow_threshold_ms = slow_threshold_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.enabled:
            return await call_next(request)

        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        event = "slow_request" if duration_ms >= self.slow_threshold_ms else "request_timing"
        logger.info(
            event,
            duration_ms=duration_ms,
            status_code=response.status_code,
            path=request.url.path,
            method=request.method,
        )
        response.headers["X-Response-Time-ms"] = str(duration_ms)
        return response
