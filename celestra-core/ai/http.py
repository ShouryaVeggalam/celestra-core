"""AI HTTP API — platform endpoints for completions, embeddings, prompts."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from ai.dependencies import provide_ai_service
from ai.schemas import (
    CompleteRequest,
    CompleteResponse,
    EmbedRequest,
    EmbedResponse,
    RenderPromptRequest,
    RenderPromptResponse,
)
from ai.service import AIService
from auth.dependencies import get_current_user
from auth.models import User

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/providers")
async def list_providers(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIService, Depends(provide_ai_service)],
) -> list[dict[str, Any]]:
    return service.list_providers()


@router.get("/prompts")
async def list_prompts(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIService, Depends(provide_ai_service)],
) -> list[dict[str, str]]:
    return service.list_prompts()


@router.post("/complete", response_model=CompleteResponse)
async def complete(
    payload: CompleteRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIService, Depends(provide_ai_service)],
) -> CompleteResponse:
    return await service.complete(payload)


@router.post("/embed", response_model=EmbedResponse)
async def embed(
    payload: EmbedRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIService, Depends(provide_ai_service)],
) -> EmbedResponse:
    return await service.embed(payload)


@router.post("/prompts/render", response_model=RenderPromptResponse)
async def render_prompt(
    payload: RenderPromptRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIService, Depends(provide_ai_service)],
) -> RenderPromptResponse:
    return service.render_prompt(payload)
