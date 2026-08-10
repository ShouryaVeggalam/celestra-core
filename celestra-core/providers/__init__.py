"""
Providers module — pluggable LLM adapters behind a stable interface.

Product apps never call OpenAI/Anthropic SDKs directly; they go through
`ai.AIService`, which routes to providers registered here.
"""

from providers.base import LLMProvider
from providers.factory import build_provider_registry
from providers.registry import ProviderRegistry
from providers.types import (
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    Message,
    Role,
    ToolSpec,
    Usage,
)

__all__ = [
    "CompletionRequest",
    "CompletionResponse",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "LLMProvider",
    "Message",
    "ProviderRegistry",
    "Role",
    "ToolSpec",
    "Usage",
    "build_provider_registry",
]
