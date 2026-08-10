"""
AI module — model routing, completions, embeddings, prompt-driven generation.

Product apps import AIService rather than calling provider SDKs directly.
"""

from __future__ import annotations

from typing import Any

from ai.router import ModelRouter
from ai.schemas import CompleteRequest, CompleteResponse, EmbedRequest, EmbedResponse
from ai.service import AIService

__all__ = [
    "AIService",
    "CompleteRequest",
    "CompleteResponse",
    "EmbedRequest",
    "EmbedResponse",
    "ModelRouter",
    "ai_router",
]


def __getattr__(name: str) -> Any:
    if name == "ai_router":
        from ai.http import router as ai_router

        return ai_router
    raise AttributeError(f"module 'ai' has no attribute {name!r}")
