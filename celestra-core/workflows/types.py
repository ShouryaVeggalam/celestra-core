"""Workflow domain types."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from shared.utils.dates import utcnow
from shared.utils.ids import new_uuid


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepDefinition(BaseModel):
    name: str
    handler: str  # registered step handler name
    input_map: dict[str, str] = Field(default_factory=dict)  # dest_key -> context path
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinition(BaseModel):
    name: str
    description: str = ""
    steps: list[StepDefinition]
    metadata: dict[str, Any] = Field(default_factory=dict)


class StepRun(BaseModel):
    name: str
    handler: str
    status: StepStatus = StepStatus.PENDING
    input: dict[str, Any] = Field(default_factory=dict)
    output: Any = None
    error: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class WorkflowRun(BaseModel):
    id: str = Field(default_factory=lambda: str(new_uuid()))
    workflow: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    input: dict[str, Any] = Field(default_factory=dict)
    output: Any = None
    context: dict[str, Any] = Field(default_factory=dict)
    steps: list[StepRun] = Field(default_factory=list)
    error: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    finished_at: datetime | None = None


class StartWorkflowRequest(BaseModel):
    workflow: str
    input: dict[str, Any] = Field(default_factory=dict)
    async_mode: bool = False  # if True and Celery available, enqueue


class WorkflowRunResponse(BaseModel):
    id: str
    workflow: str
    status: WorkflowStatus
    output: Any = None
    error: str | None = None
    steps: list[StepRun] = Field(default_factory=list)
