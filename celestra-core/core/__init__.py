"""
Celestra Core kernel.

Application factory, dependency container, health endpoints, and DI wiring.
Imports are lazy to avoid circular dependencies with capability modules.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "create_app",
    "Container",
    "get_container",
]


def __getattr__(name: str) -> Any:
    if name == "create_app":
        from core.app import create_app

        return create_app
    if name == "Container":
        from core.container import Container

        return Container
    if name == "get_container":
        from core.container import get_container

        return get_container
    raise AttributeError(f"module 'core' has no attribute {name!r}")
