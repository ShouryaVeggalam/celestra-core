"""Fail-soft operation timing — structured logs + Prometheus, never breaks business ops."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Iterator

from monitoring.application_context import normalize_application_label
from monitoring.errors import bridge_result_category, categorize_error
from shared.logging.context import get_request_id
from shared.logging.setup import get_logger

logger = get_logger(__name__)


@dataclass
class OperationState:
    """Mutable bag for callers to attach safe, non-PII fields before exit."""

    success: bool | None = None
    error_category: str | None = None
    result: str | None = None
    fields: dict[str, Any] = field(default_factory=dict)

    def set(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if key == "success":
                self.success = bool(value)
            elif key == "error_category":
                self.error_category = str(value) if value is not None else None
            elif key == "result":
                self.result = str(value) if value is not None else None
            else:
                self.fields[key] = value


def _emit_operation(
    *,
    operation: str,
    duration_ms: float,
    success: bool,
    error_category: str | None,
    result: str,
    application: str | None,
    provider: str | None,
    backend: str | None,
    model: str | None,
    extra: dict[str, Any],
) -> None:
    """Emit log + metrics. Must never raise to callers."""
    try:
        app_label = normalize_application_label(application)
        request_id = None
        try:
            request_id = get_request_id()
        except Exception:
            request_id = None

        payload: dict[str, Any] = {
            "operation": operation,
            "application": application or app_label,
            "duration_ms": duration_ms,
            "success": success,
            "result": result,
        }
        if error_category:
            payload["error_category"] = error_category
        if request_id:
            payload["request_id"] = request_id
        if provider:
            payload["provider"] = provider
        if backend:
            payload["backend"] = backend
        if model:
            payload["model"] = model
        # Only allow known-safe extra keys (no content / secrets).
        for key, value in extra.items():
            if key in {
                "provisioned",
                "prompt_name",
                "kind",
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
            }:
                payload[key] = value

        logger.info("operation_completed", **payload)

        try:
            from monitoring.metrics import get_metrics

            get_metrics().track_operation(
                operation=operation,
                application=app_label,
                result=result,
                duration_seconds=duration_ms / 1000.0,
                provider=provider,
            )
        except Exception:
            pass
    except Exception:
        pass


def _finalize(
    *,
    operation: str,
    started: float,
    state: OperationState,
    exc: BaseException | None,
    application: str | None,
    provider: str | None,
    backend: str | None,
    model: str | None,
    result_mapper: str | None,
) -> None:
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    success = state.success if state.success is not None else exc is None
    error_category = state.error_category
    if not success and error_category is None and exc is not None:
        error_category = categorize_error(exc)

    app = application
    if state.fields.get("application") is not None:
        app = str(state.fields["application"])

    if state.result is not None:
        result = state.result
    elif result_mapper == "bridge":
        result = bridge_result_category(exc, success=success)
    elif success:
        result = "ok"
    else:
        result = error_category or "internal_error"

    _emit_operation(
        operation=operation,
        duration_ms=duration_ms,
        success=success,
        error_category=error_category,
        result=result,
        application=app,
        provider=provider,
        backend=backend,
        model=model,
        extra=state.fields,
    )


@asynccontextmanager
async def timed_operation(
    operation: str,
    *,
    application: str | None = None,
    provider: str | None = None,
    backend: str | None = None,
    model: str | None = None,
    result_mapper: str | None = None,
) -> AsyncIterator[OperationState]:
    """
    Async fail-soft timer.

    Observability failures are swallowed. Business exceptions always propagate.
    """
    started = time.perf_counter()
    state = OperationState()
    held: BaseException | None = None
    try:
        yield state
    except BaseException as exc:
        held = exc
        raise
    finally:
        _finalize(
            operation=operation,
            started=started,
            state=state,
            exc=held,
            application=application,
            provider=provider,
            backend=backend,
            model=model,
            result_mapper=result_mapper,
        )


@contextmanager
def timed_operation_sync(
    operation: str,
    *,
    application: str | None = None,
    provider: str | None = None,
    backend: str | None = None,
    model: str | None = None,
    result_mapper: str | None = None,
) -> Iterator[OperationState]:
    """Sync fail-soft timer (e.g. prompt render)."""
    started = time.perf_counter()
    state = OperationState()
    held: BaseException | None = None
    try:
        yield state
    except BaseException as exc:
        held = exc
        raise
    finally:
        _finalize(
            operation=operation,
            started=started,
            state=state,
            exc=held,
            application=application,
            provider=provider,
            backend=backend,
            model=model,
            result_mapper=result_mapper,
        )
