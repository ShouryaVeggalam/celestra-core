"""Provider registry — name → LLMProvider lookup."""

from __future__ import annotations

from providers.base import LLMProvider
from providers.exceptions import ProviderNotFoundError


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, LLMProvider] = {}

    def register(self, provider: LLMProvider, *, name: str | None = None) -> None:
        key = (name or provider.name).lower()
        self._providers[key] = provider

    def get(self, name: str) -> LLMProvider:
        key = name.lower()
        if key not in self._providers:
            raise ProviderNotFoundError(
                f"Provider '{name}' is not registered",
                details={"available": sorted(self._providers)},
            )
        return self._providers[key]

    def has(self, name: str) -> bool:
        return name.lower() in self._providers

    def list(self) -> list[str]:
        return sorted(self._providers)

    def all(self) -> dict[str, LLMProvider]:
        return dict(self._providers)

    async def aclose(self) -> None:
        for provider in self._providers.values():
            await provider.aclose()
