"""Structured monitoring events for platform observability."""

from __future__ import annotations

from typing import Any

from shared.logging.setup import get_logger
from monitoring.metrics import get_metrics
from monitoring.tracing import current_trace_context

logger = get_logger(__name__)


def emit_event(name: str, *, level: str = "info", **fields: Any) -> None:
    """Emit a structured monitoring event (log + optional metric side-effects)."""
    payload = {**current_trace_context(), **fields, "event": name}
    log_fn = getattr(logger, level, logger.info)
    log_fn(name, **payload)

    if name.startswith("error.") or fields.get("error_code"):
        get_metrics().track_error(str(fields.get("error_code") or name))
