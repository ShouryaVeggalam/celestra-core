"""Request-scoped logging context helpers."""

from __future__ import annotations

from typing import Any

import structlog


def bind_context(**kwargs: Any) -> None:
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    structlog.contextvars.clear_contextvars()


def get_request_id() -> str | None:
    ctx = structlog.contextvars.get_contextvars()
    value = ctx.get("request_id")
    return str(value) if value is not None else None
