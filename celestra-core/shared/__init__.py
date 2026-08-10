"""Shared cross-cutting concerns for Celestra Core."""

from shared.exceptions.base import (
    CelestraError,
    ConflictError,
    NotFoundError,
    ValidationAppError,
    UnauthorizedError,
    ForbiddenError,
    RateLimitError,
    ExternalServiceError,
)

__all__ = [
    "CelestraError",
    "ConflictError",
    "NotFoundError",
    "ValidationAppError",
    "UnauthorizedError",
    "ForbiddenError",
    "RateLimitError",
    "ExternalServiceError",
]
