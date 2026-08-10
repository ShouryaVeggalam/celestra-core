"""Agent service facade for product applications."""

from __future__ import annotations

from agents.runtime import AgentRegistry, AgentRuntime
from agents.tools import ToolRegistry
from agents.types import AgentRunRequest, AgentRunResult, AgentSpec


class AgentService:
    def __init__(self, runtime: AgentRuntime, agents: AgentRegistry, tools: ToolRegistry) -> None:
        self.runtime = runtime
        self.agents = agents
        self.tools = tools

    def register_agent(self, spec: AgentSpec) -> None:
        self.agents.register(spec)

    def list_agents(self) -> list[AgentSpec]:
        return self.agents.list()

    def list_tools(self) -> list[dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self.tools.list()]

    async def run(self, request: AgentRunRequest) -> AgentRunResult:
        return await self.runtime.run(
            agent_name=request.agent,
            user_input=request.input,
            session_id=request.session_id,
            model=request.model,
        )
