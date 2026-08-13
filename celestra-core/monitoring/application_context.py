"""Bounded application labels for metrics and logging context."""

from __future__ import annotations

from config.applications import metric_application_label
from shared.logging.context import bind_context

# Re-export for callers that imported KNOWN_APPLICATIONS historically.
KNOWN_APPLICATIONS = frozenset({"revenue", "hiring", "finance", "chrona", "default"})


def normalize_application_label(application: str | None) -> str:
    """Map application to a bounded metrics label (never free-form)."""
    return metric_application_label(application)


def bind_application(application: str | None) -> str | None:
    """Bind application into structlog context when known. Fail-soft."""
    if application is None:
        return None
    value = str(application).strip()
    if not value:
        return None
    try:
        bind_context(application=value)
    except Exception:
        pass
    return value
