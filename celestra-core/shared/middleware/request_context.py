"""Request context middleware — assigns request_id and binds logging context."""

from __future__ import annotations

import re
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from shared.logging.context import bind_context, clear_context
from shared.logging.setup import get_logger

logger = get_logger(__name__)

# Reject free-form / oversized ids to avoid log injection and header abuse.
_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._\-]{1,128}$")


def resolve_request_id(incoming: str | None) -> str:
    """Accept a valid X-Request-ID or generate a UUID."""
    if incoming and _REQUEST_ID_RE.fullmatch(incoming.strip()):
        return incoming.strip()
    return str(uuid.uuid4())


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, *, log_requests: bool = True) -> None:
        super().__init__(app)
        self.log_requests = log_requests

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = resolve_request_id(request.headers.get("X-Request-ID"))
        request.state.request_id = request_id
        # Primary correlation id. Trace middleware may set trace_id = request_id
        # unless an explicit X-Trace-ID is provided.
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
