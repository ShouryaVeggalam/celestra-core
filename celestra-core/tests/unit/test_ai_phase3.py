"""Unit tests — providers, prompts, AI facade (Phase 3)."""

from __future__ import annotations

import pytest

from ai.router import ModelRouter
from ai.schemas import CompleteRequest, EmbedRequest, RenderPromptRequest
from ai.service import AIService
from prompts.loader import build_prompt_registry
from prompts.template import PromptTemplate
from providers.mock import MockProvider
from providers.registry import ProviderRegistry
from providers.types import Message, Role
from shared.exceptions.base import ValidationAppError


@pytest.fixture
def ai_service() -> AIService:
    registry = ProviderRegistry()
    registry.register(MockProvider())
    prompts = build_prompt_registry()
    router = ModelRouter(registry, default_provider="mock")
    return AIService(
        registry=registry,
        router=router,
        prompts=prompts,
        default_model="mock-chat",
    )


@pytest.mark.asyncio
async def test_mock_complete(ai_service: AIService):
    result = await ai_service.complete(
        CompleteRequest(messages=[Message(role=Role.USER, content="hello platform")])
    )
    assert result.provider == "mock"
    assert "hello platform" in result.content
    assert result.usage["total_tokens"] > 0


@pytest.mark.asyncio
async def test_mock_embed(ai_service: AIService):
    result = await ai_service.embed(EmbedRequest(input=["alpha", "beta"]))
    assert result.provider == "mock"
    assert len(result.embeddings) == 2
    assert result.dimensions == 8


@pytest.mark.asyncio
async def test_complete_with_prompt_name(ai_service: AIService):
    result = await ai_service.complete(
        CompleteRequest(
            prompt_name="analysis.summarize",
            prompt_variables={"content": "Celestra builds AI platforms."},
            model="mock-chat",
        )
    )
    assert "Celestra builds AI platforms." in result.content


def test_prompt_render_and_missing_vars(ai_service: AIService):
    rendered = ai_service.render_prompt(
        RenderPromptRequest(name="chat.user_turn", variables={"question": "What is Core?"})
    )
    assert "What is Core?" in rendered.content

    with pytest.raises(ValidationAppError):
        ai_service.render_prompt(RenderPromptRequest(name="chat.user_turn", variables={}))


def test_model_router_patterns():
    registry = ProviderRegistry()
    registry.register(MockProvider())
    router = ModelRouter(registry, default_provider="mock")
    assert router.resolve_provider_name("gpt-4o-mini") == "openai"
    assert router.resolve_provider_name("claude-3-5-sonnet") == "anthropic"
    assert router.resolve_provider_name("mock-chat") == "mock"
    # Falls back to mock when openai not registered
    provider, name = router.resolve("gpt-4o")
    assert name == "mock"
    assert provider.name == "mock"


def test_prompt_registry_versions():
    registry = build_prompt_registry()
    registry.register(
        PromptTemplate(name="demo", version="1", template="v1 {{ name }}", required_variables=["name"]),
        overwrite=True,
    )
    registry.register(
        PromptTemplate(name="demo", version="2", template="v2 {{ name }}", required_variables=["name"]),
        overwrite=True,
    )
    assert registry.get("demo", version="1").render({"name": "x"}) == "v1 x"
    assert registry.get("demo").render({"name": "x"}) == "v2 x"


def test_library_prompts_loaded():
    registry = build_prompt_registry()
    names = set(registry.names())
    assert "hiring.screen_resume" in names
    assert "research.company_brief" in names
    text = registry.render(
        "hiring.screen_resume",
        {
            "job_title": "Engineer",
            "job_description": "Build platforms",
            "resume_text": "Did things",
        },
    )
    assert "Engineer" in text
