"""Memory HTTP API — conversation + semantic recall."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from auth.dependencies import get_current_user
from auth.models import User
from core.container import Container, get_container
from memory.service import MemoryService
from memory.types import ConversationSession, MemoryMessage, VectorSearchHit
from shared.exceptions.base import ValidationAppError

router = APIRouter(prefix="/memory", tags=["memory"])


def provide_memory_service(container: Annotated[Container, Depends(get_container)]) -> MemoryService:
    try:
        service = container.resolve("memory_service")
    except KeyError as exc:
        raise ValidationAppError("Memory service is not initialized") from exc
    assert isinstance(service, MemoryService)
    return service


class StartSessionRequest(BaseModel):
    session_id: str | None = None


class AddMessageRequest(BaseModel):
    session_id: str
    role: str = "user"
    content: str


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
) -> ConversationSession:
    return await service.start_session(session_id=payload.session_id, user_id=str(user.id))


@router.post("/messages", response_model=ConversationSession)
async def add_message(
    payload: AddMessageRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[MemoryService, Depends(provide_memory_service)],
) -> ConversationSession:
    await service.start_session(session_id=payload.session_id)
    return await service.add_message(payload.session_id, payload.role, payload.content)


@router.get("/sessions/{session_id}/messages", response_model=list[MemoryMessage])
async def get_messages(
    session_id: str,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[MemoryService, Depends(provide_memory_service)],
) -> list[MemoryMessage]:
    return await service.get_messages(session_id)


@router.post("/remember")
async def remember(
    payload: RememberRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[MemoryService, Depends(provide_memory_service)],
) -> dict[str, Any]:
    record = await service.remember_text(payload.text, metadata=payload.metadata)
    return {"id": record.id, "text": record.text, "metadata": record.metadata}


@router.post("/recall", response_model=list[VectorSearchHit])
async def recall(
    payload: RecallRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[MemoryService, Depends(provide_memory_service)],
) -> list[VectorSearchHit]:
    return await service.recall(payload.query, top_k=payload.top_k)
