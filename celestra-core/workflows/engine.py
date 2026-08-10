"""In-process workflow engine — sequential durable-style runs (Temporal-lite)."""

from __future__ import annotations

import inspect
from typing import Any

from shared.logging.setup import get_logger
from shared.utils.dates import utcnow
from workflows.context import build_step_input
from workflows.registry import StepHandlerRegistry, WorkflowRegistry
from workflows.base_store import WorkflowRunStoreBase
from workflows.types import StepRun, StepStatus, WorkflowRun, WorkflowStatus

logger = get_logger(__name__)


class WorkflowEngine:
    def __init__(
        self,
        *,
        workflows: WorkflowRegistry,
        handlers: StepHandlerRegistry,
        store: WorkflowRunStoreBase,
    ) -> None:
        self.workflows = workflows
        self.handlers = handlers
        self.store = store

    async def start(self, workflow_name: str, input_data: dict[str, Any] | None = None) -> WorkflowRun:
        definition = self.workflows.get(workflow_name)
        run = WorkflowRun(
            workflow=definition.name,
            status=WorkflowStatus.RUNNING,
            input=input_data or {},
            context={"input": input_data or {}, "steps": {}},
            steps=[
                StepRun(name=step.name, handler=step.handler, status=StepStatus.PENDING)
                for step in definition.steps
            ],
        )
        await self.store.save(run)
        return await self._execute(run, definition.steps)

    async def _execute(self, run: WorkflowRun, steps: list) -> WorkflowRun:
        try:
            for index, step_def in enumerate(steps):
                step_run = run.steps[index]
                step_run.status = StepStatus.RUNNING
                step_run.started_at = utcnow()
                step_input = build_step_input(step_def.input_map, run.context)
                step_run.input = step_input
                await self.store.save(run)

                handler = self.handlers.get(step_def.handler)
                result = handler(step_input, {**step_def.config, "workflow": run.workflow, "run_id": run.id})
                if inspect.isawaitable(result):
                    result = await result

                step_run.output = result
                step_run.status = StepStatus.COMPLETED
                step_run.finished_at = utcnow()
                run.context["steps"][step_def.name] = {"output": result, "input": step_input}
                await self.store.save(run)

            run.status = WorkflowStatus.COMPLETED
            last = run.steps[-1].output if run.steps else None
            run.output = last
            run.finished_at = utcnow()
            await self.store.save(run)
            logger.info("workflow_completed", workflow=run.workflow, run_id=run.id)
            return run
        except Exception as exc:
            run.status = WorkflowStatus.FAILED
            run.error = str(exc)
            run.finished_at = utcnow()
            # mark current running step failed
            for step in run.steps:
                if step.status == StepStatus.RUNNING:
                    step.status = StepStatus.FAILED
                    step.error = str(exc)
                    step.finished_at = utcnow()
            await self.store.save(run)
            logger.exception("workflow_failed", workflow=run.workflow, run_id=run.id, error=str(exc))
            return run
