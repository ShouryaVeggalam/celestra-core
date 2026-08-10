"""Model router — maps model names to provider names."""

from __future__ import annotations

import re

from providers.exceptions import ModelNotRoutableError
from providers.registry import ProviderRegistry


class ModelRouter:
    """
    Route a logical model id to a registered provider.

    Default rules:
    - mock-* → mock
    - gpt-*, o1-*, o3-*, text-embedding-* → openai
    - claude-* → anthropic
    - explicit overrides via routes map
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        *,
        default_provider: str = "mock",
        routes: dict[str, str] | None = None,
    ) -> None:
        self.registry = registry
        self.default_provider = default_provider
        self.routes = {k.lower(): v.lower() for k, v in (routes or {}).items()}
        self._patterns: list[tuple[re.Pattern[str], str]] = [
            (re.compile(r"^mock", re.I), "mock"),
            (re.compile(r"^(gpt-|o1|o3|chatgpt|text-embedding)", re.I), "openai"),
            (re.compile(r"^claude", re.I), "anthropic"),
        ]

    def resolve_provider_name(self, model: str | None) -> str:
        if model:
            key = model.lower()
            if key in self.routes:
                return self.routes[key]
            for pattern, provider in self._patterns:
                if pattern.search(key):
                    return provider
        return self.default_provider

    def resolve(self, model: str | None):
        name = self.resolve_provider_name(model)
        if not self.registry.has(name):
            # Fall back to default if preferred provider unavailable
            if self.registry.has(self.default_provider):
                return self.registry.get(self.default_provider), self.default_provider
            raise ModelNotRoutableError(
                f"No provider available for model '{model}'",
                details={"wanted": name, "available": self.registry.list()},
            )
        return self.registry.get(name), name
