"""Lightweight validation helpers."""

from __future__ import annotations

from shared.exceptions.base import ValidationAppError


def require_non_empty(value: str | None, field: str = "value") -> str:
    if value is None or not str(value).strip():
        raise ValidationAppError(f"{field} must not be empty", details={"field": field})
    return str(value).strip()


def clamp(value: int | float, minimum: int | float, maximum: int | float) -> int | float:
    if minimum > maximum:
        raise ValidationAppError(
            "minimum must be <= maximum",
            details={"minimum": minimum, "maximum": maximum},
        )
    return max(minimum, min(maximum, value))
