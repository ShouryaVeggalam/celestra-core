"""Agents HTTP API."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from agents.service import AgentService
from agents.types import AgentRunRequest, AgentRunResult, AgentSpec
from auth.dependencies import get_current_user
from auth.models import User
from core.container import Container, get_container
from shared.exceptions.base import ValidationAppError

router = APIRouter(prefix="/agents", tags=["agents"])


def provide_agent_service(container: Annotated[Container, Depends(get_container)]) -> AgentService:
    try:
        service = container.resolve("agent_service")
    except KeyError as exc:
        raise ValidationAppError("Agent service is not initialized") from exc
    assert isinstance(service, AgentService)
    return service


@router.get("")
async def list_agents(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[AgentService, Depends(provide_agent_service)],
) -> list[AgentSpec]:
    return service.list_agents()


@router.get("/tools")
async def list_tools(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[AgentService, Depends(provide_agent_service)],
) -> list[dict[str, str]]:
    return service.list_tools()


@router.post("/run", response_model=AgentRunResult)
async def run_agent(
    payload: AgentRunRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[AgentService, Depends(provide_agent_service)],
) -> AgentRunResult:
    return await service.run(payload)
