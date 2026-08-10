"""Workflow and step handler registries."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from shared.exceptions.base import NotFoundError
from workflows.types import WorkflowDefinition

StepHandler = Callable[[dict[str, Any], dict[str, Any]], Any] | Callable[
    [dict[str, Any], dict[str, Any]], Awaitable[Any]
]


class StepHandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, StepHandler] = {}

    def register(self, name: str, handler: StepHandler) -> None:
        self._handlers[name] = handler

    def handler(self, name: str) -> Callable[[StepHandler], StepHandler]:
        def decorator(fn: StepHandler) -> StepHandler:
            self.register(name, fn)
            return fn

        return decorator

    def get(self, name: str) -> StepHandler:
        if name not in self._handlers:
            raise NotFoundError(f"Step handler '{name}' not found", details={"available": sorted(self._handlers)})
        return self._handlers[name]

    def list(self) -> list[str]:
        return sorted(self._handlers)


class WorkflowRegistry:
    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}

    def register(self, definition: WorkflowDefinition) -> None:
        self._workflows[definition.name] = definition

    def get(self, name: str) -> WorkflowDefinition:
        if name not in self._workflows:
            raise NotFoundError(f"Workflow '{name}' not found", details={"available": sorted(self._workflows)})
        return self._workflows[name]

    def list(self) -> list[WorkflowDefinition]:
        return sorted(self._workflows.values(), key=lambda w: w.name)
