"""Lightweight tracing context for correlation across logs and metrics."""

from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Any

import structlog

_trace_id: ContextVar[str | None] = ContextVar("celestra_trace_id", default=None)
_span_id: ContextVar[str | None] = ContextVar("celestra_span_id", default=None)


def new_trace_id() -> str:
    return uuid.uuid4().hex


def new_span_id() -> str:
    return uuid.uuid4().hex[:16]


def start_trace(trace_id: str | None = None, span_id: str | None = None) -> tuple[str, str]:
    tid = trace_id or new_trace_id()
    sid = span_id or new_span_id()
    _trace_id.set(tid)
    _span_id.set(sid)
    structlog.contextvars.bind_contextvars(trace_id=tid, span_id=sid)
    return tid, sid


def get_trace_id() -> str | None:
    return _trace_id.get()


def get_span_id() -> str | None:
    return _span_id.get()


def clear_trace() -> None:
    _trace_id.set(None)
    _span_id.set(None)


def trace_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    tid = get_trace_id()
    sid = get_span_id()
    if tid:
        headers["X-Trace-ID"] = tid
    if sid:
        headers["X-Span-ID"] = sid
    return headers


def current_trace_context() -> dict[str, Any]:
    return {"trace_id": get_trace_id(), "span_id": get_span_id()}
