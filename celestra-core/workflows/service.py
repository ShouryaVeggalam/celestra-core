"""Workflow service facade."""

from __future__ import annotations

from typing import Any

from shared.logging.setup import get_logger
from workflows.engine import WorkflowEngine
from workflows.registry import WorkflowRegistry
from workflows.base_store import WorkflowRunStoreBase
from workflows.types import StartWorkflowRequest, WorkflowDefinition, WorkflowRun

logger = get_logger(__name__)


class WorkflowService:
    def __init__(
        self,
        *,
        engine: WorkflowEngine,
        workflows: WorkflowRegistry,
        store: WorkflowRunStoreBase,
        celery_enabled: bool = False,
    ) -> None:
        self.engine = engine
        self.workflows = workflows
        self.store = store
        self.celery_enabled = celery_enabled

    def list_workflows(self) -> list[WorkflowDefinition]:
        return self.workflows.list()

    async def start(self, request: StartWorkflowRequest) -> WorkflowRun:
        if request.async_mode and self.celery_enabled:
            try:
                from workflows.tasks import run_workflow_task

                async_result = run_workflow_task.delay(request.workflow, request.input)
                # Worker + API share runs when workflow_run_backend=redis.
                logger.info("workflow_enqueued", workflow=request.workflow, task_id=async_result.id)
            except Exception as exc:
                logger.warning("workflow_enqueue_failed_falling_back", error=str(exc))
        return await self.engine.start(request.workflow, request.input)

    async def get_run(self, run_id: str) -> WorkflowRun:
        return await self.store.get(run_id)

    async def list_runs(self, *, workflow: str | None = None) -> list[WorkflowRun]:
        return await self.store.list(workflow=workflow)
