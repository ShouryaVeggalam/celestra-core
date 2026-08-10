"""Built-in platform tools."""

from __future__ import annotations

from agents.tools import ToolRegistry
from shared.utils.dates import to_iso, utcnow


def register_builtin_tools(registry: ToolRegistry) -> ToolRegistry:
    @registry.tool(description="Echo text back unchanged. Useful for smoke tests.")
    def echo(text: str) -> dict[str, str]:
        return {"echo": text}

    @registry.tool(description="Return the current UTC time in ISO-8601.")
    def current_time() -> dict[str, str]:
        return {"utc": to_iso(utcnow())}

    @registry.tool(description="Add two numbers and return the sum.")
    def add(a: float, b: float) -> dict[str, float]:
        return {"sum": float(a) + float(b)}

    return registry
