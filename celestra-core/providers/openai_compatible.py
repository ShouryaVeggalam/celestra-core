"""OpenAI-compatible chat/embeddings provider (OpenAI, Azure OpenAI-compatible, local gateways)."""

from __future__ import annotations

from typing import Any

import httpx

from providers.base import LLMProvider
from providers.exceptions import ProviderError
from providers.types import (
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ToolCall,
    Usage,
)
from shared.utils.retry import retry_async


class OpenAICompatibleProvider(LLMProvider):
    name = "openai"
    supports_tools = True
    supports_embeddings = True

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        default_model: str = "gpt-4o-mini",
        default_embedding_model: str = "text-embedding-3-small",
        timeout: float = 60.0,
        max_retries: int = 2,
        provider_name: str = "openai",
    ) -> None:
        self.name = provider_name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.default_embedding_model = default_embedding_model
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        model = request.model or self.default_model
        body: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": (m.role.value if hasattr(m.role, "value") else m.role), "content": m.content}
                for m in request.messages
            ],
        }
        if request.temperature is not None:
            body["temperature"] = request.temperature
        if request.max_tokens is not None:
            body["max_tokens"] = request.max_tokens
        if request.tools:
            body["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in request.tools
            ]

        async def _call() -> httpx.Response:
            response = await self._client.post("/chat/completions", json=body)
            if response.status_code >= 500:
                response.raise_for_status()
            return response

        try:
            response = await retry_async(_call, attempts=self.max_retries + 1)
        except Exception as exc:
            raise ProviderError(f"OpenAI completion failed: {exc}", details={"provider": self.name}) from exc

        if response.status_code >= 400:
            raise ProviderError(
                f"OpenAI completion error: {response.status_code}",
                details={"provider": self.name, "body": _safe_json(response)},
            )

        data = response.json()
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage_raw = data.get("usage") or {}
        tool_calls = [
            ToolCall(
                id=tc.get("id", ""),
                name=(tc.get("function") or {}).get("name", ""),
                arguments=(tc.get("function") or {}).get("arguments", "{}"),
            )
            for tc in message.get("tool_calls") or []
        ]
        return CompletionResponse(
            content=message.get("content") or "",
            model=data.get("model") or model,
            provider=self.name,
            finish_reason=choice.get("finish_reason"),
            usage=Usage(
                prompt_tokens=int(usage_raw.get("prompt_tokens") or 0),
                completion_tokens=int(usage_raw.get("completion_tokens") or 0),
                total_tokens=int(usage_raw.get("total_tokens") or 0),
            ),
            tool_calls=tool_calls,
            raw=data,
        )

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model = request.model or self.default_embedding_model
        body = {"model": model, "input": request.input}

        async def _call() -> httpx.Response:
            response = await self._client.post("/embeddings", json=body)
            if response.status_code >= 500:
                response.raise_for_status()
            return response

        try:
            response = await retry_async(_call, attempts=self.max_retries + 1)
        except Exception as exc:
            raise ProviderError(f"OpenAI embeddings failed: {exc}", details={"provider": self.name}) from exc

        if response.status_code >= 400:
            raise ProviderError(
                f"OpenAI embeddings error: {response.status_code}",
                details={"provider": self.name, "body": _safe_json(response)},
            )

        data = response.json()
        items = sorted(data.get("data") or [], key=lambda x: x.get("index", 0))
        usage_raw = data.get("usage") or {}
        return EmbeddingResponse(
            embeddings=[item.get("embedding") or [] for item in items],
            model=data.get("model") or model,
            provider=self.name,
            usage=Usage(
                prompt_tokens=int(usage_raw.get("prompt_tokens") or 0),
                total_tokens=int(usage_raw.get("total_tokens") or usage_raw.get("prompt_tokens") or 0),
            ),
            raw=data,
        )


def _safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except Exception:
        return response.text
