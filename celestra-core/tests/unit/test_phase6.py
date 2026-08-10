"""Unit tests — billing, analytics, SDK (Phase 6)."""

from __future__ import annotations

import pytest

from agents.builtin import register_builtin_tools
from agents.runtime import AgentRegistry, AgentRuntime
from agents.service import AgentService
from agents.tools import ToolRegistry
from agents.types import AgentSpec
from ai.router import ModelRouter
from ai.schemas import CompleteRequest
from ai.service import AIService
from analytics.service import AnalyticsService
from analytics.types import EventQuery, TrackEventRequest
from billing.service import BillingService
from billing.types import AssignPlanRequest, RecordUsageRequest
from knowledge.service import KnowledgeService
from memory.buffer import InMemoryConversationStore
from memory.conversation import ConversationMemory
from memory.service import MemoryService
from memory.vector import InMemoryVectorStore
from notifications.factory import build_notification_service
from prompts.loader import build_prompt_registry
from providers.mock import MockProvider
from providers.registry import ProviderRegistry
from providers.types import Message, Role
from sdk.local import CelestraSDK
from shared.exceptions.base import ForbiddenError
from storage.memory_store import InMemoryObjectStore
from storage.service import StorageService
from workflows.bootstrap import build_workflow_stack
from workflows.service import WorkflowService


@pytest.fixture
def billing() -> BillingService:
    return BillingService(default_plan_id="free")


def test_plans_and_default_subscription(billing: BillingService):
    plans = billing.list_plans()
    assert {p.id for p in plans} >= {"free", "pro", "enterprise"}
    sub = billing.get_subscription("acct_1")
    assert sub.plan_id == "free"


def test_usage_and_entitlements(billing: BillingService):
    billing.assign_plan(AssignPlanRequest(account_id="acct_2", plan_id="free"))
    billing.record_usage(
        RecordUsageRequest(account_id="acct_2", metric="ai.requests_per_day", quantity=99)
    )
    check = billing.check_entitlement("acct_2", "ai.requests_per_day")
    assert check.allowed is True
    assert check.remaining == 1

    billing.record_usage(
        RecordUsageRequest(account_id="acct_2", metric="ai.requests_per_day", quantity=1)
    )
    denied = billing.check_entitlement("acct_2", "ai.requests_per_day")
    assert denied.allowed is False
    with pytest.raises(ForbiddenError):
        billing.require_entitlement("acct_2", "ai.requests_per_day")


def test_boolean_entitlement(billing: BillingService):
    billing.assign_plan(AssignPlanRequest(account_id="acct_3", plan_id="free"))
    assert billing.check_entitlement("acct_3", "agents.enabled").allowed is True
    assert billing.check_entitlement("acct_3", "sso.enabled").allowed is False


def test_analytics_track_and_query():
    analytics = AnalyticsService()
    analytics.track(TrackEventRequest(name="app.opened", account_id="a1", user_id="u1"))
    analytics.track(TrackEventRequest(name="ai.complete", account_id="a1"))
    analytics.track(TrackEventRequest(name="ai.complete", account_id="a2"))
    events = analytics.query(EventQuery(name="ai.complete", account_id="a1"))
    assert len(events) == 1
    counts = analytics.counts(account_id="a1")
    assert {c.name: c.count for c in counts}["ai.complete"] == 1


@pytest.mark.asyncio
async def test_local_sdk_complete_tracks_usage_and_analytics():
    registry = ProviderRegistry()
    registry.register(MockProvider())
    ai = AIService(
        registry=registry,
        router=ModelRouter(registry),
        prompts=build_prompt_registry(),
    )
    memory = MemoryService(
        conversations=ConversationMemory(InMemoryConversationStore()),
        vectors=InMemoryVectorStore(),
        ai=ai,
    )
    tools = ToolRegistry()
    register_builtin_tools(tools)
    agents = AgentRegistry()
    agents.register(AgentSpec(name="assistant", tools=["echo"], max_steps=2))
    agent_service = AgentService(
        AgentRuntime(ai=ai, tools=tools, agents=agents, memory=memory),
        agents,
        tools,
    )
    engine, workflows, _ = build_workflow_stack()
    sdk = CelestraSDK(
        ai=ai,
        memory=memory,
        agents=agent_service,
        workflows=WorkflowService(engine=engine, workflows=workflows, store=engine.store),
        storage=StorageService(InMemoryObjectStore()),
        notifications=build_notification_service(),
        knowledge=KnowledgeService(ai=ai, vectors=InMemoryVectorStore()),
        billing=BillingService(),
        analytics=AnalyticsService(),
    )
    result = await sdk.complete(
        CompleteRequest(messages=[Message(role=Role.USER, content="hello sdk")])
    )
    assert "hello sdk" in result.content
    usage = sdk.billing.usage_summary("default", metric="ai.requests_per_day")
    assert usage and usage[0].total == 1
    tracked = sdk.analytics.query(EventQuery(name="ai.complete"))
    assert tracked
