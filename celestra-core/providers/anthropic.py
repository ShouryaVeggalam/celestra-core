"""Anthropic Messages API provider."""

from __future__ import annotations

from typing import Any

import httpx

from providers.base import LLMProvider
from providers.exceptions import ProviderError
from providers.types import CompletionRequest, CompletionResponse, Usage
from shared.utils.retry import retry_async


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    supports_tools = False
    supports_embeddings = False

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.anthropic.com",
        default_model: str = "claude-3-5-sonnet-20241022",
        timeout: float = 60.0,
        max_retries: int = 2,
        api_version: str = "2023-06-01",
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "x-api-key": api_key,
                "anthropic-version": api_version,
                "Content-Type": "application/json",
            },
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        model = request.model or self.default_model
        system_parts: list[str] = []
        messages: list[dict[str, str]] = []
        for message in request.messages:
            role = message.role.value if hasattr(message.role, "value") else str(message.role)
            if role == "system":
                system_parts.append(message.content)
            elif role in {"user", "assistant"}:
                messages.append({"role": role, "content": message.content})

        if not messages:
            raise ProviderError("Anthropic requires at least one user/assistant message")

        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or 1024,
        }
        if system_parts:
            body["system"] = "\n\n".join(system_parts)
        if request.temperature is not None:
            body["temperature"] = request.temperature

        async def _call() -> httpx.Response:
            response = await self._client.post("/v1/messages", json=body)
            if response.status_code >= 500:
                response.raise_for_status()
            return response

        try:
            response = await retry_async(_call, attempts=self.max_retries + 1)
        except Exception as exc:
            raise ProviderError(f"Anthropic completion failed: {exc}") from exc

        if response.status_code >= 400:
            try:
                err_body = response.json()
            except Exception:
                err_body = response.text
            raise ProviderError(
                f"Anthropic completion error: {response.status_code}",
                details={"body": err_body},
            )

        data = response.json()
        content_blocks = data.get("content") or []
        text = "".join(block.get("text", "") for block in content_blocks if block.get("type") == "text")
        usage_raw = data.get("usage") or {}
        prompt_tokens = int(usage_raw.get("input_tokens") or 0)
        completion_tokens = int(usage_raw.get("output_tokens") or 0)
        return CompletionResponse(
            content=text,
            model=data.get("model") or model,
            provider=self.name,
            finish_reason=data.get("stop_reason"),
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            raw=data,
        )
