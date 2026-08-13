"""Stable observability error categories mapped from Core exceptions."""

from __future__ import annotations

from shared.exceptions.base import (
    CelestraError,
    ConfigurationError,
    ConflictError,
    ExternalServiceError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
    ValidationAppError,
)

# Bounded vocabulary for structured logs / metrics `result` when failed.
ERROR_CATEGORIES = frozenset(
    {
        "validation_error",
        "authentication_error",
        "authorization_error",
        "not_found",
        "conflict",
        "configuration_error",
        "external_service_error",
        "provider_error",
        "dependency_unavailable",
        "timeout",
        "internal_error",
    }
)

_CODE_TO_CATEGORY: dict[str, str] = {
    "validation_error": "validation_error",
    "not_found": "not_found",
    "conflict": "conflict",
    "unauthorized": "authentication_error",
    "invalid_token": "authentication_error",
    "forbidden": "authorization_error",
    "configuration_error": "configuration_error",
    "external_service_error": "external_service_error",
    "rate_limit_exceeded": "external_service_error",
    "celestra_error": "internal_error",
    "http_error": "internal_error",
    "internal_error": "internal_error",
}


def categorize_error(exc: BaseException) -> str:
    """Map an exception to a stable, low-cardinality error category."""
    if isinstance(exc, ValidationAppError):
        return "validation_error"
    if isinstance(exc, UnauthorizedError):
        return "authentication_error"
    if isinstance(exc, ForbiddenError):
        return "authorization_error"
    if isinstance(exc, NotFoundError):
        return "not_found"
    if isinstance(exc, ConflictError):
        return "conflict"
    if isinstance(exc, ConfigurationError):
        return "configuration_error"
    if isinstance(exc, ExternalServiceError):
        return "external_service_error"
    if isinstance(exc, RateLimitError):
        return "external_service_error"
    if isinstance(exc, CelestraError):
        return _CODE_TO_CATEGORY.get(exc.code, "internal_error")
    if isinstance(exc, (TimeoutError,)):
        return "timeout"
    name = type(exc).__name__
    if "Timeout" in name:
        return "timeout"
    if name in {"ConnectionError", "ConnectionRefusedError", "OSError"}:
        return "dependency_unavailable"
    if "Provider" in name or "APIError" in name:
        return "provider_error"
    return "internal_error"


def bridge_result_category(exc: BaseException | None, *, success: bool) -> str:
    """Bounded bridge exchange result label (ok / unauthorized / replay / …)."""
    if success or exc is None:
        return "ok"
    msg = str(exc).lower()
    if isinstance(exc, UnauthorizedError):
        if "replay" in msg:
            return "replay"
        return "unauthorized"
    if isinstance(exc, ForbiddenError):
        if "mismatch" in msg:
            return "mismatch"
        if "disabled" in msg:
            return "disabled"
        return "unauthorized"
    if isinstance(exc, ConfigurationError):
        return "configuration_error"
    if isinstance(exc, ValidationAppError):
        return "unauthorized"
    return "internal_error"
