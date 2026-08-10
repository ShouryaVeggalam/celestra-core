"""Exception hierarchy for consistent API error responses."""

from __future__ import annotations

from typing import Any


class CelestraError(Exception):
    """Base platform exception."""

    code: str = "celestra_error"
    status_code: int = 500
    message: str = "An unexpected error occurred"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.code = code or self.__class__.code
        self.status_code = status_code or self.__class__.status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"error": {"code": self.code, "message": self.message}}
        if self.details:
            payload["error"]["details"] = self.details
        return payload


class ValidationAppError(CelestraError):
    code = "validation_error"
    status_code = 422
    message = "Validation failed"


class NotFoundError(CelestraError):
    code = "not_found"
    status_code = 404
    message = "Resource not found"


class ConflictError(CelestraError):
    code = "conflict"
    status_code = 409
    message = "Resource conflict"


class UnauthorizedError(CelestraError):
    code = "unauthorized"
    status_code = 401
    message = "Authentication required"


class ForbiddenError(CelestraError):
    code = "forbidden"
    status_code = 403
    message = "Insufficient permissions"


class RateLimitError(CelestraError):
    code = "rate_limit_exceeded"
    status_code = 429
    message = "Rate limit exceeded"


class ExternalServiceError(CelestraError):
    code = "external_service_error"
    status_code = 502
    message = "Upstream service failed"


class ConfigurationError(CelestraError):
    code = "configuration_error"
    status_code = 500
    message = "Platform configuration is incomplete"
