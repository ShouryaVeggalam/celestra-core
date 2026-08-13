"""Memory HTTP API — conversation + semantic recall (ownership enforced)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from auth.dependencies import get_current_user
from auth.models import User
from config.settings import Settings, get_settings
from core.container import Container, get_container
from memory.conversation import normalize_application
from memory.service import MemoryService
from memory.types import DEFAULT_APPLICATION, ConversationSession, MemoryMessage, VectorSearchHit
from monitoring.application_context import bind_application
from monitoring.operations import timed_operation
from shared.exceptions.base import ValidationAppError

router = APIRouter(prefix="/memory", tags=["memory"])


def provide_memory_service(container: Annotated[Container, Depends(get_container)]) -> MemoryService:
    try:
        service = container.resolve("memory_service")
    except KeyError as exc:
        raise ValidationAppError("Memory service is not initialized") from exc
    assert isinstance(service, MemoryService)
    return service


def _conversation_backend(settings: Settings) -> str:
    return settings.memory_conversation_backend


class StartSessionRequest(BaseModel):
    session_id: str | None = None
    application: str = DEFAULT_APPLICATION


class AddMessageRequest(BaseModel):
    session_id: str
    role: str = "user"
    content: str
    application: str = DEFAULT_APPLICATION


class RememberRequest(BaseModel):
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecallRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=50)


@router.post("/sessions", response_model=ConversationSession)
async def start_session(
    payload: StartSessionRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[MemoryService, Depends(provide_memory_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ConversationSession:
    app = normalize_application(payload.application)
    bind_application(app)
    # Privacy: never log message content. user_id/session_id stay in logs only (not metrics).
    async with timed_operation(
        "memory_session_start",
        application=app,
        backend=_conversation_backend(settings),
    ):
        return await service.start_session(
            session_id=payload.session_id,
            user_id=str(user.id),
            application=app,
        )


@router.post("/messages", response_model=ConversationSession)
async def add_message(
    payload: AddMessageRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[MemoryService, Depends(provide_memory_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ConversationSession:
    app = normalize_application(payload.application)
    bind_application(app)
    # Ownership enforced in service; does not auto-create sessions.
    # Do not log payload.content.
    async with timed_operation(
        "memory_append",
        application=app,
        backend=_conversation_backend(settings),
    ):
        return await service.add_message(
            payload.session_id,
            payload.role,
            payload.content,
            user_id=str(user.id),
            application=app,
        )


@router.get("/sessions/{session_id}/messages", response_model=list[MemoryMessage])
async def get_messages(
    session_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[MemoryService, Depends(provide_memory_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    application: str = Query(default=DEFAULT_APPLICATION),
) -> list[MemoryMessage]:
    app = normalize_application(application)
    bind_application(app)
    async with timed_operation(
        "memory_get",
        application=app,
        backend=_conversation_backend(settings),
    ):
        return await service.get_messages(
            session_id,
            user_id=str(user.id),
            application=app,
        )


@router.post("/remember")
async def remember(
    payload: RememberRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[MemoryService, Depends(provide_memory_service)],
) -> dict[str, Any]:
    # Vector memory remains unscoped by user/application — not multi-user safe.
    record = await service.remember_text(payload.text, metadata=payload.metadata)
    return {"id": record.id, "text": record.text, "metadata": record.metadata}


@router.post("/recall", response_model=list[VectorSearchHit])
async def recall(
    payload: RecallRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[MemoryService, Depends(provide_memory_service)],
) -> list[VectorSearchHit]:
    # Vector memory remains unscoped by user/application — not multi-user safe.
    return await service.recall(payload.query, top_k=payload.top_k)
