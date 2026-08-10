"""
Workflows module — sequential workflow engine + Celery foundation.

Product apps define workflows here instead of inventing their own job graphs.
"""

from __future__ import annotations

from typing import Any

from workflows.engine import WorkflowEngine
from workflows.registry import StepHandlerRegistry, WorkflowRegistry
from workflows.service import WorkflowService
from workflows.types import (
    StartWorkflowRequest,
    StepDefinition,
    WorkflowDefinition,
    WorkflowRun,
    WorkflowStatus,
)

__all__ = [
    "StartWorkflowRequest",
    "StepDefinition",
    "StepHandlerRegistry",
    "WorkflowDefinition",
    "WorkflowEngine",
    "WorkflowRegistry",
    "WorkflowRun",
    "WorkflowService",
    "WorkflowStatus",
    "workflows_router",
]


def __getattr__(name: str) -> Any:
    if name == "workflows_router":
        from workflows.http import router as workflows_router

        return workflows_router
    raise AttributeError(name)
