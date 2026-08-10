"""
Agents module — tool registry and agent runtime for Celestra apps.

Product apps register tools/agents here instead of building their own loops.
"""

from __future__ import annotations

from typing import Any

from agents.runtime import AgentRegistry, AgentRuntime
from agents.service import AgentService
from agents.tools import Tool, ToolRegistry
from agents.types import AgentRunRequest, AgentRunResult, AgentSpec, AgentStep

__all__ = [
    "AgentRegistry",
    "AgentRunRequest",
    "AgentRunResult",
    "AgentRuntime",
    "AgentService",
    "AgentSpec",
    "AgentStep",
    "Tool",
    "ToolRegistry",
    "agents_router",
]


def __getattr__(name: str) -> Any:
    if name == "agents_router":
        from agents.http import router as agents_router

        return agents_router
    raise AttributeError(name)
