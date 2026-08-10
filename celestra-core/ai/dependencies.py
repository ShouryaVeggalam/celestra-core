"""FastAPI dependencies for the AI facade."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from ai.service import AIService
from core.container import Container, get_container
from shared.exceptions.base import ValidationAppError


def provide_ai_service(container: Annotated[Container, Depends(get_container)]) -> AIService:
    try:
        service = container.resolve("ai_service")
    except KeyError as exc:
        raise ValidationAppError("AI service is not initialized") from exc
    if not isinstance(service, AIService):
        raise ValidationAppError("AI service registration is invalid")
    return service
