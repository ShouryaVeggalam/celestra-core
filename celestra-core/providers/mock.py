"""Deterministic mock provider — local/dev/tests without API keys."""

from __future__ import annotations

import hashlib
from collections.abc import AsyncIterator

from providers.base import LLMProvider
from providers.types import (
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    Usage,
)


def _role_value(role: object) -> str:
    return role.value if hasattr(role, "value") else str(role)


class MockProvider(LLMProvider):
    name = "mock"
    supports_tools = True
    supports_embeddings = True

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        model = request.model or "mock-chat"
        last_user = ""
        for message in reversed(request.messages):
            if _role_value(message.role) == "user":
                last_user = message.content
                break

        content = f"[mock:{model}] {last_user}".strip()
        prompt_tokens = sum(len(m.content.split()) for m in request.messages)
        completion_tokens = max(len(content.split()), 1)
        return CompletionResponse(
            content=content,
            model=model,
            provider=self.name,
            finish_reason="stop",
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            raw={"mock": True},
        )

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        result = await self.complete(request)
        for token in result.content.split(" "):
            yield token + " "

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model = request.model or "mock-embed"
        inputs = request.input if isinstance(request.input, list) else [request.input]
        vectors: list[list[float]] = []
        for text in inputs:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            vec = [((b / 255.0) * 2) - 1 for b in digest[:8]]
            vectors.append(vec)
        tokens = sum(len(t.split()) for t in inputs)
        return EmbeddingResponse(
            embeddings=vectors,
            model=model,
            provider=self.name,
            usage=Usage(prompt_tokens=tokens, total_tokens=tokens),
            raw={"mock": True, "dims": 8},
        )
