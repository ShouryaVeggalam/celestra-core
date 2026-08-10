"""HTTP/API schemas for the AI facade."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from providers.types import Message, ToolSpec


class CompleteRequest(BaseModel):
    messages: list[Message] | None = None
    prompt: str | None = None
    system: str | None = None
    model: str | None = None
    provider: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)
    tools: list[ToolSpec] | None = None
    # Prompt registry integration
    prompt_name: str | None = None
    prompt_version: str | None = None
    prompt_variables: dict[str, Any] = Field(default_factory=dict)


class CompleteResponse(BaseModel):
    content: str
    model: str
    provider: str
    finish_reason: str | None = None
    usage: dict[str, int]
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)


class EmbedRequest(BaseModel):
    input: str | list[str]
    model: str | None = None
    provider: str | None = None


class EmbedResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
    provider: str
    usage: dict[str, int]
    dimensions: int


class RenderPromptRequest(BaseModel):
    name: str
    version: str | None = None
    variables: dict[str, Any] = Field(default_factory=dict)


class RenderPromptResponse(BaseModel):
    name: str
    version: str
    content: str


class ModelInfo(BaseModel):
    provider: str
    supports_tools: bool
    supports_embeddings: bool
