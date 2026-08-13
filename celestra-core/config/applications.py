"""Approved Celestra application identities — server-side registry.

New application IDs require an explicit Core configuration / deployment change.
Arbitrary client-supplied application strings are not accepted for bridge or
tenant-scoped memory.
"""

from __future__ import annotations

from shared.exceptions.base import ValidationAppError

# Product applications that may use the identity bridge and multi-tenant memory.
APPROVED_APPLICATIONS: frozenset[str] = frozenset(
    {
        "revenue",
        "hiring",
        "finance",
        "chrona",
    }
)

# Memory may also use "default" for unscoped / single-tenant local use.
MEMORY_APPLICATIONS: frozenset[str] = APPROVED_APPLICATIONS | {"default"}

# Prometheus / observability labels (includes unknown for out-of-band values).
METRIC_APPLICATION_LABELS: frozenset[str] = MEMORY_APPLICATIONS | {"unknown"}

# Default issuer claim expected per application (overridable via settings).
DEFAULT_BRIDGE_ISSUERS: dict[str, str] = {
    "revenue": "revenue-ai",
    "hiring": "hiring-ai",
    "finance": "finance-ai",
    "chrona": "chrona-ai",
}


def normalize_application_id(value: str | None) -> str:
    return (value or "").strip().lower()


def is_approved_application(application: str | None) -> bool:
    return normalize_application_id(application) in APPROVED_APPLICATIONS


def require_approved_application(application: str | None) -> str:
    """Validate bridge / product application id. Raises ValidationAppError."""
    app = normalize_application_id(application)
    if not app:
        raise ValidationAppError(
            "application is required",
            details={"field": "application"},
        )
    if app not in APPROVED_APPLICATIONS:
        raise ValidationAppError(
            "application is not an approved Celestra application",
            details={"application": app, "allowed": sorted(APPROVED_APPLICATIONS)},
        )
    return app


def require_memory_application(application: str | None) -> str:
    """Validate memory application (approved products + default)."""
    app = normalize_application_id(application) or "default"
    if app not in MEMORY_APPLICATIONS:
        raise ValidationAppError(
            "application is not allowed for memory",
            details={"application": app, "allowed": sorted(MEMORY_APPLICATIONS)},
        )
    return app


def metric_application_label(application: str | None) -> str:
    app = normalize_application_id(application)
    if not app:
        return "default"
    if app in MEMORY_APPLICATIONS:
        return app
    return "unknown"
