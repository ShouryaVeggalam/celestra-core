"""In-memory workflow run store."""

from __future__ import annotations

from shared.exceptions.base import NotFoundError
from shared.utils.dates import utcnow
from workflows.base_store import WorkflowRunStoreBase
from workflows.types import WorkflowRun


class WorkflowRunStore(WorkflowRunStoreBase):
    """In-process store — default for tests / single worker."""

    def __init__(self) -> None:
        self._runs: dict[str, WorkflowRun] = {}

    async def save(self, run: WorkflowRun) -> WorkflowRun:
        run.updated_at = utcnow()
        self._runs[run.id] = run.model_copy(deep=True)
        return run.model_copy(deep=True)

    async def get(self, run_id: str) -> WorkflowRun:
        run = self._runs.get(run_id)
        if run is None:
            raise NotFoundError(f"Workflow run '{run_id}' not found")
        return run.model_copy(deep=True)

    async def list(self, *, workflow: str | None = None, limit: int = 50) -> list[WorkflowRun]:
        runs = list(self._runs.values())
        if workflow:
            runs = [r for r in runs if r.workflow == workflow]
        runs.sort(key=lambda r: r.created_at, reverse=True)
        return [r.model_copy(deep=True) for r in runs[:limit]]
