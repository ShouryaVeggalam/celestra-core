"""Built-in step handlers and demo workflows."""

from __future__ import annotations

from typing import Any

from workflows.registry import StepHandlerRegistry, WorkflowRegistry
from workflows.types import StepDefinition, WorkflowDefinition


def register_builtin_steps(handlers: StepHandlerRegistry) -> StepHandlerRegistry:
    @handlers.handler("set_value")
    async def set_value(step_input: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        value = config.get("value", step_input)
        return {"value": value}

    @handlers.handler("merge")
    async def merge(step_input: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        return {**step_input, **(config.get("extra") or {})}

    @handlers.handler("format_message")
    async def format_message(step_input: dict[str, Any], config: dict[str, Any]) -> dict[str, str]:
        template = config.get("template", "Hello {name}")
        return {"message": template.format(**step_input)}

    @handlers.handler("uppercase")
    async def uppercase(step_input: dict[str, Any], config: dict[str, Any]) -> dict[str, str]:
        key = config.get("field", "message")
        text = str(step_input.get(key, ""))
        return {key: text.upper()}

    return handlers


def register_builtin_workflows(workflows: WorkflowRegistry) -> WorkflowRegistry:
    workflows.register(
        WorkflowDefinition(
            name="demo.greeting",
            description="Demo sequential workflow: format then uppercase a greeting",
            steps=[
                StepDefinition(
                    name="format",
                    handler="format_message",
                    input_map={"name": "input.name"},
                    config={"template": "Hello {name}, welcome to Celestra Core"},
                ),
                StepDefinition(
                    name="shout",
                    handler="uppercase",
                    input_map={"message": "steps.format.output.message"},
                    config={"field": "message"},
                ),
            ],
        )
    )
    return workflows
