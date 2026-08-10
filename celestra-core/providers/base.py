"""LLM provider interface — all adapters implement this contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from providers.types import CompletionRequest, CompletionResponse, EmbeddingRequest, EmbeddingResponse


class LLMProvider(ABC):
    """Stable provider contract used by the AI facade and model router."""

    name: str
    supports_tools: bool = False
    supports_embeddings: bool = False

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Run a chat completion."""

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """Optional token stream. Default: yield full completion content once."""
        result = await self.complete(request)
        yield result.content

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError(f"Provider '{self.name}' does not support embeddings")

    async def aclose(self) -> None:
        """Release HTTP clients / resources."""
        return None
