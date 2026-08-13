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
from monitoring.operations import timed_operation, timed_operation_sync
from prompts.registry import PromptRegistry
from providers.registry import ProviderRegistry
from providers.types import CompletionRequest, EmbeddingRequest, Message, Role
from shared.exceptions.base import ValidationAppError


def _current_application() -> str | None:
    try:
        import structlog

        ctx = structlog.contextvars.get_contextvars()
        value = ctx.get("application")
        return str(value) if value is not None else None
    except Exception:
        return None


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

        application = _current_application()
        started = time.perf_counter()
        async with timed_operation(
            "ai_complete",
            application=application,
            provider=provider_name,
            model=model,
        ) as op:
            try:
                result = await provider.complete(completion)
            except Exception:
                self._track_ai(
                    provider=provider_name,
                    kind="complete",
                    success=False,
                    seconds=time.perf_counter() - started,
                )
                raise
            # Token usage only when the provider already exposes reliable values.
            usage_fields: dict[str, Any] = {}
            if result.usage is not None:
                if result.usage.prompt_tokens is not None:
                    usage_fields["prompt_tokens"] = result.usage.prompt_tokens
                if result.usage.completion_tokens is not None:
                    usage_fields["completion_tokens"] = result.usage.completion_tokens
                if result.usage.total_tokens is not None:
                    usage_fields["total_tokens"] = result.usage.total_tokens
            if usage_fields:
                op.set(**usage_fields)
            self._track_ai(
                provider=provider_name,
                kind="complete",
                success=True,
                seconds=time.perf_counter() - started,
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

        application = _current_application()
        started = time.perf_counter()
        async with timed_operation(
            "ai_embed",
            application=application,
            provider=provider_name,
            model=model,
        ):
            try:
                result = await provider.embed(EmbeddingRequest(input=request.input, model=model))
            except Exception:
                self._track_ai(
                    provider=provider_name,
                    kind="embed",
                    success=False,
                    seconds=time.perf_counter() - started,
                )
                raise
            self._track_ai(
                provider=provider_name,
                kind="embed",
                success=True,
                seconds=time.perf_counter() - started,
            )

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
        application = _current_application()
        with timed_operation_sync(
            "prompt_render",
            application=application,
        ) as op:
            template = self.prompts.get(request.name, version=request.version)
            # prompt_name is safe for logs (catalog key); not used as a Prometheus label.
            op.set(prompt_name=template.name)
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
            return [message for message in request.messages]

        messages: list[Message] = []
        if request.system:
            messages.append(Message(role=Role.SYSTEM, content=request.system))

        user_content: str | None = request.prompt
        if request.prompt_name:
            application = _current_application()
            with timed_operation_sync(
                "prompt_render",
                application=application,
            ) as op:
                op.set(prompt_name=request.prompt_name)
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
            if hasattr(metrics, "ai_request_duration_seconds") and seconds > 0:
                metrics.ai_request_duration_seconds.labels(provider=provider, kind=kind).observe(seconds)
        except Exception:
            pass
