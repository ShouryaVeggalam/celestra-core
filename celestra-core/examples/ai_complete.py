"""
Example: product apps use AIService + prompts (never raw provider SDKs).

    python examples/ai_complete.py
"""

from __future__ import annotations

import asyncio

from ai.router import ModelRouter
from ai.schemas import CompleteRequest, EmbedRequest
from ai.service import AIService
from prompts.loader import build_prompt_registry
from providers.mock import MockProvider
from providers.registry import ProviderRegistry
from providers.types import Message, Role


async def main() -> None:
    registry = ProviderRegistry()
    registry.register(MockProvider())
    service = AIService(
        registry=registry,
        router=ModelRouter(registry),
        prompts=build_prompt_registry(),
        default_model="mock-chat",
    )

    completion = await service.complete(
        CompleteRequest(
            messages=[
                Message(role=Role.SYSTEM, content="You are Celestra Core."),
                Message(role=Role.USER, content="Say hello to Hiring AI."),
            ]
        )
    )
    print("complete:", completion.content)

    prompted = await service.complete(
        CompleteRequest(
            prompt_name="analysis.summarize",
            prompt_variables={"content": "Phase 3 adds providers, AI facade, and prompts."},
        )
    )
    print("prompted:", prompted.content)

    embedded = await service.embed(EmbedRequest(input="celestra core"))
    print("embed dims:", embedded.dimensions, "provider:", embedded.provider)


if __name__ == "__main__":
    asyncio.run(main())
