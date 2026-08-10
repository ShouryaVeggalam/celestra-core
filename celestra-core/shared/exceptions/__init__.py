"""Custom exception hierarchy for Celestra Core."""

from shared.exceptions.base import (
    CelestraError,
    ConflictError,
    NotFoundError,
    ValidationAppError,
    UnauthorizedError,
    ForbiddenError,
    RateLimitError,
    ExternalServiceError,
    ConfigurationError,
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
    "ConfigurationError",
]
