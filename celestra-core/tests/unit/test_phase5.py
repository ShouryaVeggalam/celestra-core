"""Unit tests — storage, notifications, knowledge (Phase 5)."""

from __future__ import annotations

import pytest

from ai.router import ModelRouter
from ai.service import AIService
from knowledge.chunking import chunk_text
from knowledge.service import KnowledgeService
from knowledge.types import IngestTextRequest, QueryRequest
from notifications.factory import build_notification_service
from notifications.types import NotificationChannel, SendNotificationRequest
from prompts.loader import build_prompt_registry
from providers.mock import MockProvider
from providers.registry import ProviderRegistry
from storage.memory_store import InMemoryObjectStore
from storage.service import StorageService
from memory.vector import InMemoryVectorStore


@pytest.fixture
def ai_service() -> AIService:
    registry = ProviderRegistry()
    registry.register(MockProvider())
    return AIService(
        registry=registry,
        router=ModelRouter(registry, default_provider="mock"),
        prompts=build_prompt_registry(),
    )


@pytest.mark.asyncio
async def test_storage_upload_download_delete():
    store = StorageService(InMemoryObjectStore())
    info = await store.upload("docs/a.txt", b"hello core", content_type="text/plain")
    assert info.key == "docs/a.txt"
    assert info.size == 10
    assert await store.exists("docs/a.txt")
    obj = await store.download("docs/a.txt")
    assert obj.data == b"hello core"
    url = await store.signed_url("docs/a.txt")
    assert "docs/a.txt" in url
    await store.delete("docs/a.txt")
    assert not await store.exists("docs/a.txt")


def test_chunk_text():
    text = "a" * 50
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert len(chunks) >= 2
    assert all(len(c) <= 20 for c in chunks)
    with pytest.raises(ValueError):
        chunk_text("x", chunk_size=10, overlap=10)


@pytest.mark.asyncio
async def test_notifications_email_and_inbox():
    service = build_notification_service()
    email = await service.send(
        SendNotificationRequest(
            channel=NotificationChannel.EMAIL,
            recipient="ops@celestra.dev",
            subject="Hello",
            body="Phase 5 online",
        )
    )
    assert email.status.value == "sent"

    in_app = await service.send(
        SendNotificationRequest(
            channel="in_app",
            recipient="user-1",
            body="Welcome",
            user_id="user-1",
        )
    )
    assert in_app.status.value == "sent"
    inbox = service.list_inbox("user-1")
    assert len(inbox) == 1
    assert inbox[0].body == "Welcome"


@pytest.mark.asyncio
async def test_knowledge_ingest_and_query(ai_service: AIService):
    storage = StorageService(InMemoryObjectStore())
    knowledge = KnowledgeService(
        ai=ai_service,
        vectors=InMemoryVectorStore(),
        storage=storage,
        chunk_size=200,
        chunk_overlap=20,
    )
    knowledge.create_knowledge_base("platform", "Celestra platform docs")
    doc = await knowledge.ingest_text(
        IngestTextRequest(
            knowledge_base="platform",
            title="About Core",
            content=(
                "Celestra Core is an enterprise AI platform foundation. "
                "It provides auth, AI providers, agents, workflows, memory, storage, "
                "notifications, and knowledge RAG for every Celestra application."
            ),
        )
    )
    assert doc.title == "About Core"
    assert await storage.exists(f"knowledge/{doc.knowledge_base_id}/{doc.id}.txt")

    result = await knowledge.query(
        QueryRequest(
            knowledge_base="platform",
            question="Celestra Core is an enterprise AI platform foundation.",
            top_k=3,
        )
    )
    assert result.knowledge_base == "platform"
    assert result.sources
    assert "Celestra" in result.answer or result.provider == "mock"
