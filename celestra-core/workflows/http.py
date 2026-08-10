"""Workflows HTTP API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from auth.models import User
from core.container import Container, get_container
from shared.exceptions.base import ValidationAppError
from workflows.service import WorkflowService
from workflows.types import StartWorkflowRequest, WorkflowDefinition, WorkflowRun, WorkflowRunResponse

router = APIRouter(prefix="/workflows", tags=["workflows"])


def provide_workflow_service(container: Annotated[Container, Depends(get_container)]) -> WorkflowService:
    try:
        service = container.resolve("workflow_service")
    except KeyError as exc:
        raise ValidationAppError("Workflow service is not initialized") from exc
    assert isinstance(service, WorkflowService)
    return service


@router.get("")
async def list_workflows(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkflowService, Depends(provide_workflow_service)],
) -> list[WorkflowDefinition]:
    return service.list_workflows()


@router.post("/start", response_model=WorkflowRunResponse)
async def start_workflow(
    payload: StartWorkflowRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkflowService, Depends(provide_workflow_service)],
) -> WorkflowRun:
    return await service.start(payload)


@router.get("/runs/{run_id}", response_model=WorkflowRunResponse)
async def get_run(
    run_id: str,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkflowService, Depends(provide_workflow_service)],
) -> WorkflowRun:
    return await service.get_run(run_id)


@router.get("/runs")
async def list_runs(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkflowService, Depends(provide_workflow_service)],
    workflow: str | None = None,
) -> list[WorkflowRun]:
    return await service.list_runs(workflow=workflow)
