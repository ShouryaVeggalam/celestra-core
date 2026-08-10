"""Request context middleware — assigns request_id and binds logging context."""

from __future__ import annotations

import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from shared.logging.context import bind_context, clear_context
from shared.logging.setup import get_logger

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, *, log_requests: bool = True) -> None:
        super().__init__(app)
        self.log_requests = log_requests

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        bind_context(request_id=request_id, method=request.method, path=request.url.path)
        started = time.perf_counter()
        status_code: int | None = None
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            if self.log_requests:
                logger.info("request_completed", status_code=status_code, duration_ms=duration_ms)
            clear_context()
