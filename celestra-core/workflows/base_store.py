"""Workflow run store interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from workflows.types import WorkflowRun


class WorkflowRunStoreBase(ABC):
    @abstractmethod
    async def save(self, run: WorkflowRun) -> WorkflowRun: ...

    @abstractmethod
    async def get(self, run_id: str) -> WorkflowRun: ...

    @abstractmethod
    async def list(self, *, workflow: str | None = None, limit: int = 50) -> list[WorkflowRun]: ...
