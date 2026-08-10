"""Secrets abstraction — swap EnvSecretProvider for Vault/AWS later without touching callers."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Mapping


class SecretProvider(ABC):
    """Abstract secret store used by the configuration layer."""

    @abstractmethod
    def get(self, key: str, default: str | None = None) -> str | None:
        """Return a secret value or default if missing."""

    @abstractmethod
    def require(self, key: str) -> str:
        """Return a secret value or raise KeyError if missing."""

    def get_many(self, keys: list[str]) -> dict[str, str | None]:
        return {key: self.get(key) for key in keys}


class EnvSecretProvider(SecretProvider):
    """Reads secrets from process environment / .env."""

    def __init__(self, environ: Mapping[str, str] | None = None) -> None:
        self._environ = environ if environ is not None else os.environ

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._environ.get(key, default)

    def require(self, key: str) -> str:
        value = self._environ.get(key)
        if value is None or value == "":
            raise KeyError(f"Required secret '{key}' is not set")
        return value


class DictSecretProvider(SecretProvider):
    """In-memory provider for tests."""

    def __init__(self, values: Mapping[str, str]) -> None:
        self._values = dict(values)

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._values.get(key, default)

    def require(self, key: str) -> str:
        value = self._values.get(key)
        if value is None or value == "":
            raise KeyError(f"Required secret '{key}' is not set")
        return value
