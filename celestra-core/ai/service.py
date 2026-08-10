"""AI facade — completions, embeddings, and prompt-driven generation."""

from __future__ import annotations

import time
from typing import Any

from ai.router import ModelRouter
from ai.schemas import (
    CompleteRequest,
    CompleteResponse,
    EmbedRequest,
    EmbedResponse,
    RenderPromptRequest,
    RenderPromptResponse,
)
from prompts.registry import PromptRegistry
from providers.registry import ProviderRegistry
from providers.types import CompletionRequest, EmbeddingRequest, Message, Role
from shared.exceptions.base import ValidationAppError
from shared.logging.setup import get_logger

logger = get_logger(__name__)


class AIService:
    """
    Application-facing AI API.

    Product apps call this instead of provider SDKs.
    """

    def __init__(
        self,
        *,
        registry: ProviderRegistry,
        router: ModelRouter,
        prompts: PromptRegistry,
        default_model: str = "mock-chat",
    ) -> None:
        self.registry = registry
        self.router = router
        self.prompts = prompts
        self.default_model = default_model

    async def complete(self, request: CompleteRequest) -> CompleteResponse:
        messages = self._build_messages(request)
        model = request.model or self.default_model

        if request.provider:
            provider = self.registry.get(request.provider)
            provider_name = request.provider
        else:
            provider, provider_name = self.router.resolve(model)

        completion = CompletionRequest(
            messages=messages,
            model=model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            tools=request.tools,
        )

        started = time.perf_counter()
        try:
            result = await provider.complete(completion)
            self._track_ai(provider=provider_name, kind="complete", success=True, seconds=time.perf_counter() - started)
        except Exception:
            self._track_ai(provider=provider_name, kind="complete", success=False, seconds=time.perf_counter() - started)
            raise

        logger.info(
            "ai_complete",
            provider=result.provider,
            model=result.model,
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
        )
        return CompleteResponse(
            content=result.content,
            model=result.model,
            provider=result.provider,
            finish_reason=result.finish_reason,
            usage={
                "prompt_tokens": result.usage.prompt_tokens,
                "completion_tokens": result.usage.completion_tokens,
                "total_tokens": result.usage.total_tokens,
            },
            tool_calls=[tc.model_dump() for tc in result.tool_calls],
        )

    async def embed(self, request: EmbedRequest) -> EmbedResponse:
        model = request.model or "mock-embed"
        if request.provider:
            provider = self.registry.get(request.provider)
            provider_name = request.provider
        else:
            provider, provider_name = self.router.resolve(model)

        started = time.perf_counter()
        try:
            result = await provider.embed(EmbeddingRequest(input=request.input, model=model))
            self._track_ai(provider=provider_name, kind="embed", success=True, seconds=time.perf_counter() - started)
        except Exception:
            self._track_ai(provider=provider_name, kind="embed", success=False, seconds=time.perf_counter() - started)
            raise

        dims = len(result.embeddings[0]) if result.embeddings else 0
        return EmbedResponse(
            embeddings=result.embeddings,
            model=result.model,
            provider=result.provider,
            usage={
                "prompt_tokens": result.usage.prompt_tokens,
                "completion_tokens": result.usage.completion_tokens,
                "total_tokens": result.usage.total_tokens,
            },
            dimensions=dims,
        )

    def render_prompt(self, request: RenderPromptRequest) -> RenderPromptResponse:
        template = self.prompts.get(request.name, version=request.version)
        content = template.render(request.variables)
        return RenderPromptResponse(name=template.name, version=template.version, content=content)

    def list_providers(self) -> list[dict[str, Any]]:
        return [
            {
                "provider": name,
                "supports_tools": provider.supports_tools,
                "supports_embeddings": provider.supports_embeddings,
            }
            for name, provider in self.registry.all().items()
        ]

    def list_prompts(self) -> list[dict[str, str]]:
        return [
            {"name": t.name, "version": t.version, "description": t.description, "key": t.key}
            for t in self.prompts.list()
        ]

    def _build_messages(self, request: CompleteRequest) -> list[Message]:
        if request.messages:
            return request.messages

        messages: list[Message] = []
        if request.system:
            messages.append(Message(role=Role.SYSTEM, content=request.system))

        user_content: str | None = request.prompt
        if request.prompt_name:
            rendered = self.prompts.render(
                request.prompt_name,
                request.prompt_variables,
                version=request.prompt_version,
            )
            user_content = rendered if not user_content else f"{user_content}\n\n{rendered}"

        if not user_content:
            raise ValidationAppError(
                "Provide messages, prompt, or prompt_name",
                details={"fields": ["messages", "prompt", "prompt_name"]},
            )
        messages.append(Message(role=Role.USER, content=user_content))
        return messages

    @staticmethod
    def _track_ai(*, provider: str, kind: str, success: bool, seconds: float) -> None:
        try:
            from monitoring.metrics import get_metrics

            metrics = get_metrics()
            # Reuse error/login style counters via dynamic labels if present; else no-op safe
            if hasattr(metrics, "ai_requests_total"):
                metrics.ai_requests_total.labels(
                    provider=provider,
                    kind=kind,
                    result="success" if success else "failure",
                ).inc()
            if hasattr(metrics, "ai_request_duration_seconds"):
                metrics.ai_request_duration_seconds.labels(provider=provider, kind=kind).observe(seconds)
        except Exception:
            pass
