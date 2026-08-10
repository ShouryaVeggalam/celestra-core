"""Unit tests — memory, agents, workflows (Phase 4)."""

from __future__ import annotations

import pytest

from agents.builtin import register_builtin_tools
from agents.runtime import AgentRegistry, AgentRuntime
from agents.service import AgentService
from agents.tools import ToolRegistry
from agents.types import AgentRunRequest, AgentSpec
from ai.router import ModelRouter
from ai.service import AIService
from memory.buffer import InMemoryConversationStore
from memory.conversation import ConversationMemory
from memory.service import MemoryService
from memory.vector import InMemoryVectorStore, cosine_similarity
from prompts.loader import build_prompt_registry
from providers.mock import MockProvider
from providers.registry import ProviderRegistry
from workflows.bootstrap import build_workflow_stack
from workflows.service import WorkflowService
from workflows.types import StartWorkflowRequest, WorkflowStatus


@pytest.fixture
def ai_service() -> AIService:
    registry = ProviderRegistry()
    registry.register(MockProvider())
    return AIService(
        registry=registry,
        router=ModelRouter(registry, default_provider="mock"),
        prompts=build_prompt_registry(),
        default_model="mock-chat",
    )


@pytest.fixture
def memory_service(ai_service: AIService) -> MemoryService:
    return MemoryService(
        conversations=ConversationMemory(InMemoryConversationStore(), window_size=10),
        vectors=InMemoryVectorStore(),
        ai=ai_service,
    )


@pytest.fixture
def agent_service(ai_service: AIService, memory_service: MemoryService) -> AgentService:
    tools = ToolRegistry()
    register_builtin_tools(tools)
    agents = AgentRegistry()
    agents.register(
        AgentSpec(
            name="assistant",
            tools=["echo", "add", "current_time"],
            max_steps=4,
            system_prompt="Use CALL tool_name {json} when needed.",
        )
    )
    runtime = AgentRuntime(ai=ai_service, tools=tools, agents=agents, memory=memory_service)
    return AgentService(runtime, agents, tools)


@pytest.mark.asyncio
async def test_conversation_memory_window(memory_service: MemoryService):
    session = await memory_service.start_session(session_id="s1")
    assert session.id == "s1"
    await memory_service.add_message("s1", "user", "hello")
    await memory_service.add_message("s1", "assistant", "hi")
    messages = await memory_service.get_messages("s1")
    assert len(messages) == 2
    assert messages[0].content == "hello"


@pytest.mark.asyncio
async def test_semantic_memory_recall(memory_service: MemoryService):
    await memory_service.remember_text(
        "Celestra builds enterprise AI platforms",
        metadata={"tag": "about"},
    )
    await memory_service.remember_text("Unrelated cooking recipe for pasta")
    # Identical query → identical mock embedding → top hit is exact match
    hits = await memory_service.recall("Celestra builds enterprise AI platforms", top_k=2)
    assert hits
    assert hits[0].text.startswith("Celestra")
    assert hits[0].score == pytest.approx(1.0)


def test_cosine_similarity():
    assert cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_agent_tool_call_via_call_syntax(agent_service: AgentService):
    result = await agent_service.run(
        AgentRunRequest(agent="assistant", input='CALL echo {"text": "platform"}')
    )
    assert result.agent == "assistant"
    assert any(step.kind == "tool_call" for step in result.steps)
    assert any(step.kind == "tool_result" for step in result.steps)
    # Final step exists after tool loop
    assert result.steps[-1].kind == "final"


@pytest.mark.asyncio
async def test_agent_with_memory_session(agent_service: AgentService):
    result = await agent_service.run(
        AgentRunRequest(
            agent="assistant",
            input="hello without tools",
            session_id="agent-session-1",
        )
    )
    assert result.session_id == "agent-session-1"
    assert "hello without tools" in result.output


@pytest.mark.asyncio
async def test_workflow_demo_greeting():
    engine, workflows, _ = build_workflow_stack()
    service = WorkflowService(engine=engine, workflows=workflows, store=engine.store)
    assert any(w.name == "demo.greeting" for w in service.list_workflows())
    run = await service.start(StartWorkflowRequest(workflow="demo.greeting", input={"name": "Ada"}))
    assert run.status == WorkflowStatus.COMPLETED
    assert run.output["message"] == "HELLO ADA, WELCOME TO CELESTRA CORE"
    loaded = await service.get_run(run.id)
    assert loaded.id == run.id
    assert len(loaded.steps) == 2
