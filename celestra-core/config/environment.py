"""Environment loader — loads .env files and exposes typed environment helpers."""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


class Environment(str, Enum):
    """Supported runtime environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"

    @classmethod
    def from_value(cls, value: str | None) -> Environment:
        if not value:
            return cls.DEVELOPMENT
        normalized = value.strip().lower()
        for env in cls:
            if env.value == normalized:
                return env
        aliases = {
            "dev": cls.DEVELOPMENT,
            "local": cls.DEVELOPMENT,
            "prod": cls.PRODUCTION,
            "stage": cls.STAGING,
        }
        return aliases.get(normalized, cls.DEVELOPMENT)


def find_env_file(start: Path | None = None) -> Path | None:
    """Locate a .env file (cwd parents, then package root)."""
    package_root = Path(__file__).resolve().parents[1]
    current = (start or Path.cwd()).resolve()
    candidates = [current / ".env", *[p / ".env" for p in current.parents], package_root / ".env"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def load_environment(env_file: str | Path | None = None, *, override: bool = False) -> Path | None:
    """Load environment variables from a .env file."""
    if env_file is not None:
        path = Path(env_file)
        if not path.is_file():
            raise FileNotFoundError(f"Environment file not found: {path}")
    else:
        path = find_env_file()

    if path is not None:
        load_dotenv(path, override=override)
    return path


@lru_cache(maxsize=1)
def current_environment() -> Environment:
    raw = os.getenv("CELESTRA_ENV") or os.getenv("ENV") or "development"
    return Environment.from_value(raw)


def is_production() -> bool:
    return current_environment() is Environment.PRODUCTION


def is_development() -> bool:
    return current_environment() is Environment.DEVELOPMENT


def is_test() -> bool:
    return current_environment() is Environment.TEST
