"""JSON serialization helpers using orjson when available."""

from __future__ import annotations

from typing import Any

try:
    import orjson

    def to_json(data: Any) -> str:
        return orjson.dumps(data, default=str).decode("utf-8")

    def from_json(payload: str | bytes) -> Any:
        return orjson.loads(payload)

except ImportError:  # pragma: no cover
    import json

    def to_json(data: Any) -> str:
        return json.dumps(data, default=str)

    def from_json(payload: str | bytes) -> Any:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        return json.loads(payload)
