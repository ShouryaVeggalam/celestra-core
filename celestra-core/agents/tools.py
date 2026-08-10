"""Tool registry — callable tools agents can invoke."""

from __future__ import annotations

import inspect
import json
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, Field

from providers.types import ToolSpec
from shared.exceptions.base import NotFoundError, ValidationAppError

ToolHandler = Callable[..., Any] | Callable[..., Awaitable[Any]]


class Tool(BaseModel):
    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}})
    handler: Any = Field(exclude=True)

    model_config = {"arbitrary_types_allowed": True}

    def to_spec(self) -> ToolSpec:
        return ToolSpec(name=self.name, description=self.description, parameters=self.parameters)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def tool(
        self,
        name: str | None = None,
        *,
        description: str = "",
        parameters: dict[str, Any] | None = None,
    ) -> Callable[[ToolHandler], ToolHandler]:
        def decorator(fn: ToolHandler) -> ToolHandler:
            tool_name = name or fn.__name__
            params = parameters
            if params is None:
                params = _infer_parameters(fn)
            self.register(
                Tool(
                    name=tool_name,
                    description=description or (fn.__doc__ or "").strip(),
                    parameters=params,
                    handler=fn,
                )
            )
            return fn

        return decorator

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise NotFoundError(f"Tool '{name}' not found", details={"available": sorted(self._tools)})
        return self._tools[name]

    def list(self) -> list[Tool]:
        return sorted(self._tools.values(), key=lambda t: t.name)

    def specs(self) -> list[ToolSpec]:
        return [t.to_spec() for t in self.list()]

    async def execute(self, name: str, arguments: dict[str, Any] | str) -> Any:
        tool = self.get(name)
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments) if arguments.strip() else {}
            except json.JSONDecodeError as exc:
                raise ValidationAppError(
                    "Tool arguments must be valid JSON",
                    details={"tool": name, "arguments": arguments},
                ) from exc
        if not isinstance(arguments, dict):
            raise ValidationAppError("Tool arguments must be an object", details={"tool": name})

        result = tool.handler(**arguments)
        if inspect.isawaitable(result):
            return await result
        return result


def _infer_parameters(fn: ToolHandler) -> dict[str, Any]:
    props: dict[str, Any] = {}
    required: list[str] = []
    sig = inspect.signature(fn)
    for param_name, param in sig.parameters.items():
        if param_name in {"self", "cls"}:
            continue
        props[param_name] = {"type": "string"}
        if param.default is inspect.Parameter.empty:
            required.append(param_name)
    schema: dict[str, Any] = {"type": "object", "properties": props}
    if required:
        schema["required"] = required
    return schema
