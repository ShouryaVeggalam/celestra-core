"""Redis-backed workflow run store — shared across API and Celery workers."""

from __future__ import annotations

from shared.exceptions.base import NotFoundError
from shared.redis.client import RedisClient
from shared.utils.dates import utcnow
from workflows.base_store import WorkflowRunStoreBase
from workflows.types import WorkflowRun


class RedisWorkflowRunStore(WorkflowRunStoreBase):
    def __init__(self, redis: RedisClient, *, ttl_seconds: int = 60 * 60 * 24 * 30) -> None:
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    def _run_key(self, run_id: str) -> str:
        return self.redis.key(f"workflow:run:{run_id}")

    def _index_key(self) -> str:
        return self.redis.key("workflow:runs:index")

    async def save(self, run: WorkflowRun) -> WorkflowRun:
        run.updated_at = utcnow()
        payload = run.model_dump_json()
        pipe = self.redis.raw.pipeline()
        pipe.set(self._run_key(run.id), payload, ex=self.ttl_seconds)
        pipe.zadd(self._index_key(), {run.id: run.created_at.timestamp()})
        await pipe.execute()
        return run.model_copy(deep=True)

    async def get(self, run_id: str) -> WorkflowRun:
        raw = await self.redis.raw.get(self._run_key(run_id))
        if raw is None:
            raise NotFoundError(f"Workflow run '{run_id}' not found")
        return WorkflowRun.model_validate_json(raw)

    async def list(self, *, workflow: str | None = None, limit: int = 50) -> list[WorkflowRun]:
        ids = await self.redis.raw.zrevrange(self._index_key(), 0, max(limit * 5, limit) - 1)
        runs: list[WorkflowRun] = []
        for run_id in ids:
            raw = await self.redis.raw.get(self._run_key(run_id))
            if not raw:
                continue
            run = WorkflowRun.model_validate_json(raw)
            if workflow and run.workflow != workflow:
                continue
            runs.append(run)
            if len(runs) >= limit:
                break
        return runs
