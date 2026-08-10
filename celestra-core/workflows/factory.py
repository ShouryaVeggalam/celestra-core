"""Workflow stack factory — in-memory or Redis run stores."""

from __future__ import annotations

from config.settings import Settings
from shared.logging.setup import get_logger
from shared.redis.client import RedisClient
from workflows.base_store import WorkflowRunStoreBase
from workflows.builtin import register_builtin_steps, register_builtin_workflows
from workflows.engine import WorkflowEngine
from workflows.redis_store import RedisWorkflowRunStore
from workflows.registry import StepHandlerRegistry, WorkflowRegistry
from workflows.store import WorkflowRunStore

logger = get_logger(__name__)


def build_workflow_run_store(
    settings: Settings,
    redis: RedisClient | None = None,
) -> WorkflowRunStoreBase:
    if settings.workflow_run_backend == "redis":
        if redis is None:
            logger.warning("workflow_run_redis_unavailable_fallback_memory")
            return WorkflowRunStore()
        return RedisWorkflowRunStore(redis, ttl_seconds=settings.workflow_run_ttl_seconds)
    return WorkflowRunStore()


def build_workflow_stack(
    settings: Settings | None = None,
    redis: RedisClient | None = None,
) -> tuple[WorkflowEngine, WorkflowRegistry, StepHandlerRegistry]:
    handlers = StepHandlerRegistry()
    workflows = WorkflowRegistry()
    if settings is None:
        store: WorkflowRunStoreBase = WorkflowRunStore()
    else:
        store = build_workflow_run_store(settings, redis)
    register_builtin_steps(handlers)
    register_builtin_workflows(workflows)
    engine = WorkflowEngine(workflows=workflows, handlers=handlers, store=store)
    return engine, workflows, handlers
