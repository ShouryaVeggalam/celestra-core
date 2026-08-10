"""Celery tasks for workflow execution (workers run this module)."""

from __future__ import annotations

from typing import Any

from workflows.celery_app import celery_app


@celery_app.task(name="workflows.run")
def run_workflow_task(workflow_name: str, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Execute a workflow inside a Celery worker.

    Note: worker process must bootstrap registries the same way as the API.
    Phase 4 ships the task stub; in-process engine remains the default path.
    """
    import asyncio

    from workflows.bootstrap import build_workflow_stack

    engine, _, _ = build_workflow_stack()

    async def _run():
        run = await engine.start(workflow_name, input_data or {})
        return run.model_dump(mode="json")

    return asyncio.run(_run())
