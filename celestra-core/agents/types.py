"""Agent domain types."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from shared.utils.dates import utcnow


class AgentSpec(BaseModel):
    name: str
    description: str = ""
    system_prompt: str = "You are a helpful Celestra agent. Use tools when needed."
    tools: list[str] = Field(default_factory=list)  # empty = all registered tools
    model: str | None = None
    max_steps: int = 5
    temperature: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentStep(BaseModel):
    index: int
    kind: Literal["thought", "tool_call", "tool_result", "final"]
    content: str = ""
    tool_name: str | None = None
    tool_arguments: dict[str, Any] | None = None
    tool_result: Any = None
    created_at: datetime = Field(default_factory=utcnow)


class AgentRunRequest(BaseModel):
    agent: str
    input: str
    session_id: str | None = None
    model: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRunResult(BaseModel):
    agent: str
    output: str
    session_id: str | None = None
    steps: list[AgentStep] = Field(default_factory=list)
    model: str | None = None
    provider: str | None = None
