"""
Example: storage + notifications + knowledge (Phase 5).

    python examples/phase5_stack.py
"""

from __future__ import annotations

import asyncio

from ai.router import ModelRouter
from ai.service import AIService
from knowledge.service import KnowledgeService
from knowledge.types import IngestTextRequest, QueryRequest
from memory.vector import InMemoryVectorStore
from notifications.factory import build_notification_service
from notifications.types import SendNotificationRequest
from prompts.loader import build_prompt_registry
from providers.mock import MockProvider
from providers.registry import ProviderRegistry
from storage.memory_store import InMemoryObjectStore
from storage.service import StorageService


async def main() -> None:
    registry = ProviderRegistry()
    registry.register(MockProvider())
    ai = AIService(
        registry=registry,
        router=ModelRouter(registry),
        prompts=build_prompt_registry(),
    )
    storage = StorageService(InMemoryObjectStore())
    await storage.upload("readme.txt", b"Celestra Core Phase 5")
    print("stored:", await storage.list_keys())

    notes = build_notification_service()
    sent = await notes.send(
        SendNotificationRequest(
            channel="email",
            recipient="team@celestra.dev",
            subject="Phase 5",
            body="Storage, notifications, knowledge are ready.",
        )
    )
    print("notification:", sent.status.value, sent.id)

    knowledge = KnowledgeService(ai=ai, vectors=InMemoryVectorStore(), storage=storage)
    knowledge.create_knowledge_base("docs")
    await knowledge.ingest_text(
        IngestTextRequest(
            knowledge_base="docs",
            title="Platform",
            content="Celestra Core powers Hiring AI and Revenue AI with shared infrastructure.",
        )
    )
    answer = await knowledge.query(
        QueryRequest(
            knowledge_base="docs",
            question="Celestra Core powers Hiring AI and Revenue AI with shared infrastructure.",
        )
    )
    print("rag answer:", answer.answer)
    print("rag sources:", len(answer.sources))


if __name__ == "__main__":
    asyncio.run(main())
