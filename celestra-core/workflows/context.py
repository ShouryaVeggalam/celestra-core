"""Workflow execution context helpers."""

from __future__ import annotations

from typing import Any


def resolve_path(data: dict[str, Any], path: str) -> Any:
    """Resolve dotted path like 'input.company' or 'steps.extract.output'."""
    current: Any = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def build_step_input(input_map: dict[str, str], context: dict[str, Any]) -> dict[str, Any]:
    if not input_map:
        return dict(context.get("input") or {})
    result: dict[str, Any] = {}
    for dest, source in input_map.items():
        result[dest] = resolve_path(context, source)
    return result
