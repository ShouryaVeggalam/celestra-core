"""Shared provider request/response types — stable contract for all adapters."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    role: Role | Literal["system", "user", "assistant", "tool"]
    content: str
    name: str | None = None
    tool_call_id: str | None = None


class ToolSpec(BaseModel):
    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class CompletionRequest(BaseModel):
    messages: list[Message]
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)
    tools: list[ToolSpec] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str  # JSON string


class CompletionResponse(BaseModel):
    content: str
    model: str
    provider: str
    finish_reason: str | None = None
    usage: Usage = Field(default_factory=Usage)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class EmbeddingRequest(BaseModel):
    input: str | list[str]
    model: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
    provider: str
    usage: Usage = Field(default_factory=Usage)
    raw: dict[str, Any] = Field(default_factory=dict)
