"""Build the provider registry from platform settings."""

from __future__ import annotations

from config.settings import Settings
from providers.anthropic import AnthropicProvider
from providers.mock import MockProvider
from providers.openai_compatible import OpenAICompatibleProvider
from providers.registry import ProviderRegistry
from shared.logging.setup import get_logger

logger = get_logger(__name__)


def build_provider_registry(settings: Settings) -> ProviderRegistry:
    """
    Register available providers.

    Mock is always available. OpenAI/Anthropic register only when API keys exist.
    """
    registry = ProviderRegistry()
    registry.register(MockProvider())

    if settings.openai_api_key:
        registry.register(
            OpenAICompatibleProvider(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                default_model=settings.openai_default_model,
                default_embedding_model=settings.openai_embedding_model,
                timeout=settings.ai_timeout_seconds,
                max_retries=settings.ai_max_retries,
            )
        )
        logger.info("provider_registered", provider="openai")
    else:
        logger.info("provider_skipped", provider="openai", reason="missing_api_key")

    if settings.anthropic_api_key:
        registry.register(
            AnthropicProvider(
                api_key=settings.anthropic_api_key,
                base_url=settings.anthropic_base_url,
                default_model=settings.anthropic_default_model,
                timeout=settings.ai_timeout_seconds,
                max_retries=settings.ai_max_retries,
            )
        )
        logger.info("provider_registered", provider="anthropic")
    else:
        logger.info("provider_skipped", provider="anthropic", reason="missing_api_key")

    return registry
