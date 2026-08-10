"""Dependency injection container."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from config.settings import Settings, get_settings
from shared.redis.cache import CacheService
from shared.redis.client import RedisClient


@dataclass
class Container:
    settings: Settings
    redis: Optional[RedisClient] = None
    cache: Optional[CacheService] = None
    _extras: dict[str, object] = field(default_factory=dict)

    def register(self, name: str, service: object) -> None:
        self._extras[name] = service

    def resolve(self, name: str) -> object:
        if name not in self._extras:
            raise KeyError(f"Service '{name}' is not registered")
        return self._extras[name]

    def wire_cache(self) -> CacheService:
        if self.redis is None:
            raise RuntimeError("Redis must be initialized before wiring cache")
        self.cache = CacheService(self.redis, default_ttl=self.settings.cache_default_ttl)
        return self.cache


_container: Optional[Container] = None


def build_container(settings: Settings | None = None) -> Container:
    global _container
    _container = Container(settings=settings or get_settings())
    return _container


def get_container() -> Container:
    if _container is None:
        raise RuntimeError("Container is not initialized. Call build_container() first.")
    return _container


def reset_container() -> None:
    global _container
    _container = None
