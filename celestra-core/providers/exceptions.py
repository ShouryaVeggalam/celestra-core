"""Provider-specific errors mapped into the Celestra exception hierarchy."""

from __future__ import annotations

from shared.exceptions.base import ExternalServiceError, ValidationAppError


class ProviderError(ExternalServiceError):
    code = "provider_error"
    message = "AI provider request failed"


class ProviderNotFoundError(ValidationAppError):
    code = "provider_not_found"
    status_code = 404
    message = "AI provider not found"


class ModelNotRoutableError(ValidationAppError):
    code = "model_not_routable"
    status_code = 400
    message = "No provider registered for model"
