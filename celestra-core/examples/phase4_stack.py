"""
Example: memory + agent + workflow (Phase 4) without live API keys.

    python examples/phase4_stack.py
"""

from __future__ import annotations

import asyncio

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
from memory.vector import InMemoryVectorStore
from prompts.loader import build_prompt_registry
from providers.mock import MockProvider
from providers.registry import ProviderRegistry
from workflows.bootstrap import build_workflow_stack
from workflows.service import WorkflowService
from workflows.types import StartWorkflowRequest


async def main() -> None:
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

    await memory.remember_text("Hiring AI uses Celestra Core agents and workflows")
    hits = await memory.recall("Hiring AI agents")
    print("recall:", hits[0].text if hits else None)

    tools = ToolRegistry()
    register_builtin_tools(tools)
    agents = AgentRegistry()
    agents.register(AgentSpec(name="assistant", tools=["echo", "add"], max_steps=4))
    agent_service = AgentService(
        AgentRuntime(ai=ai, tools=tools, agents=agents, memory=memory),
        agents,
        tools,
    )
    agent_result = await agent_service.run(
        AgentRunRequest(agent="assistant", input='CALL add {"a": 2, "b": 3}', session_id="demo")
    )
    print("agent steps:", [s.kind for s in agent_result.steps])
    print("agent output:", agent_result.output)

    engine, workflows, _ = build_workflow_stack()
    wf = WorkflowService(engine=engine, workflows=workflows, store=engine.store)
    run = await wf.start(StartWorkflowRequest(workflow="demo.greeting", input={"name": "Core"}))
    print("workflow:", run.status.value, run.output)


if __name__ == "__main__":
    asyncio.run(main())
