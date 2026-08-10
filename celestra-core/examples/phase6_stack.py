"""
Example: billing + analytics + in-process SDK (Phase 6).

    python examples/phase6_stack.py
"""

from __future__ import annotations

import asyncio

from agents.builtin import register_builtin_tools
from agents.runtime import AgentRegistry, AgentRuntime
from agents.service import AgentService
from agents.tools import ToolRegistry
from agents.types import AgentSpec
from ai.router import ModelRouter
from ai.schemas import CompleteRequest
from ai.service import AIService
from analytics.service import AnalyticsService
from analytics.types import TrackEventRequest
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
from sdk import CelestraSDK
from storage.memory_store import InMemoryObjectStore
from storage.service import StorageService
from workflows.bootstrap import build_workflow_stack
from workflows.service import WorkflowService


async def main() -> None:
    registry = ProviderRegistry()
    registry.register(MockProvider())
    ai = AIService(registry=registry, router=ModelRouter(registry), prompts=build_prompt_registry())
    memory = MemoryService(
        conversations=ConversationMemory(InMemoryConversationStore()),
        vectors=InMemoryVectorStore(),
        ai=ai,
    )
    tools = ToolRegistry()
    register_builtin_tools(tools)
    agents = AgentRegistry()
    agents.register(AgentSpec(name="assistant", tools=["echo"], max_steps=2))
    engine, workflows, _ = build_workflow_stack()

    sdk = CelestraSDK(
        ai=ai,
        memory=memory,
        agents=AgentService(AgentRuntime(ai=ai, tools=tools, agents=agents, memory=memory), agents, tools),
        workflows=WorkflowService(engine=engine, workflows=workflows, store=engine.store),
        storage=StorageService(InMemoryObjectStore()),
        notifications=build_notification_service(),
        knowledge=KnowledgeService(ai=ai, vectors=InMemoryVectorStore()),
        billing=BillingService(),
        analytics=AnalyticsService(),
    )

    sdk.billing.assign_plan(AssignPlanRequest(account_id="demo", plan_id="pro"))
    print("plans:", [p.id for p in sdk.billing.list_plans()])
    print("entitlement:", sdk.check_entitlement("demo", "analytics.export").allowed)

    await sdk.complete(CompleteRequest(messages=[Message(role=Role.USER, content="phase 6")]))
    sdk.track(TrackEventRequest(name="demo.finished", account_id="demo"))
    sdk.record_usage(RecordUsageRequest(account_id="demo", metric="ai.requests_per_day", quantity=1))
    print("usage:", sdk.billing.usage_summary("demo"))
    print("analytics counts:", sdk.analytics.counts(account_id="demo"))


if __name__ == "__main__":
    asyncio.run(main())
