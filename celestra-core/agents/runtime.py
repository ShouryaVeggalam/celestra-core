"""Agent runtime — tool-calling loop over AIService + ToolRegistry + Memory."""

from __future__ import annotations

import json
from typing import Any

from agents.tools import ToolRegistry
from agents.types import AgentRunResult, AgentSpec, AgentStep
from ai.schemas import CompleteRequest
from ai.service import AIService
from memory.service import MemoryService
from providers.types import Message, Role
from shared.exceptions.base import NotFoundError, ValidationAppError
from shared.logging.setup import get_logger

logger = get_logger(__name__)


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, AgentSpec] = {}

    def register(self, spec: AgentSpec) -> None:
        self._agents[spec.name] = spec

    def get(self, name: str) -> AgentSpec:
        if name not in self._agents:
            raise NotFoundError(f"Agent '{name}' not found", details={"available": sorted(self._agents)})
        return self._agents[name]

    def list(self) -> list[AgentSpec]:
        return sorted(self._agents.values(), key=lambda a: a.name)


class AgentRuntime:
    def __init__(
        self,
        *,
        ai: AIService,
        tools: ToolRegistry,
        agents: AgentRegistry,
        memory: MemoryService | None = None,
    ) -> None:
        self.ai = ai
        self.tools = tools
        self.agents = agents
        self.memory = memory

    async def run(
        self,
        *,
        agent_name: str,
        user_input: str,
        session_id: str | None = None,
        model: str | None = None,
    ) -> AgentRunResult:
        spec = self.agents.get(agent_name)
        tool_names = spec.tools or [t.name for t in self.tools.list()]
        tool_specs = [self.tools.get(name).to_spec() for name in tool_names]

        messages: list[Message] = [Message(role=Role.SYSTEM, content=spec.system_prompt)]
        if self.memory and session_id:
            await self.memory.start_session(session_id=session_id)
            history = await self.memory.conversations.as_provider_messages(session_id)
            messages.extend(history)
            await self.memory.add_message(session_id, "user", user_input)
        messages.append(Message(role=Role.USER, content=user_input))

        steps: list[AgentStep] = []
        final_text = ""
        used_model = model or spec.model
        used_provider = None

        for step_idx in range(spec.max_steps):
            response = await self.ai.complete(
                CompleteRequest(
                    messages=messages,
                    model=used_model,
                    temperature=spec.temperature,
                    tools=tool_specs or None,
                )
            )
            used_model = response.model
            used_provider = response.provider

            if response.tool_calls:
                for call in response.tool_calls:
                    args = call.get("arguments") if isinstance(call, dict) else call.arguments
                    name = call.get("name") if isinstance(call, dict) else call.name
                    if isinstance(args, str):
                        try:
                            parsed_args = json.loads(args) if args.strip() else {}
                        except json.JSONDecodeError:
                            parsed_args = {"_raw": args}
                    else:
                        parsed_args = args or {}

                    steps.append(
                        AgentStep(
                            index=len(steps),
                            kind="tool_call",
                            content=f"Calling {name}",
                            tool_name=name,
                            tool_arguments=parsed_args,
                        )
                    )
                    try:
                        result = await self.tools.execute(name, parsed_args)
                    except Exception as exc:
                        result = {"error": str(exc)}
                    steps.append(
                        AgentStep(
                            index=len(steps),
                            kind="tool_result",
                            content=str(result),
                            tool_name=name,
                            tool_result=result,
                        )
                    )
                    messages.append(
                        Message(
                            role=Role.ASSISTANT,
                            content=response.content or f"tool_call:{name}",
                        )
                    )
                    messages.append(
                        Message(
                            role=Role.TOOL,
                            content=json.dumps(result, default=str),
                            name=name,
                        )
                    )
                continue

            # Mock / text providers: allow CALL tool JSON in content
            parsed = _parse_text_tool_call(response.content)
            if parsed and step_idx < spec.max_steps - 1:
                name, parsed_args = parsed
                if name not in tool_names:
                    raise ValidationAppError(f"Agent attempted unknown tool '{name}'")
                steps.append(
                    AgentStep(
                        index=len(steps),
                        kind="tool_call",
                        content=f"Calling {name}",
                        tool_name=name,
                        tool_arguments=parsed_args,
                    )
                )
                result = await self.tools.execute(name, parsed_args)
                steps.append(
                    AgentStep(
                        index=len(steps),
                        kind="tool_result",
                        content=str(result),
                        tool_name=name,
                        tool_result=result,
                    )
                )
                messages.append(Message(role=Role.ASSISTANT, content=response.content))
                messages.append(
                    Message(role=Role.USER, content=f"Tool {name} result: {json.dumps(result, default=str)}")
                )
                continue

            final_text = response.content
            steps.append(AgentStep(index=len(steps), kind="final", content=final_text))
            break
        else:
            final_text = final_text or "Agent stopped: max steps reached"
            steps.append(AgentStep(index=len(steps), kind="final", content=final_text))

        if self.memory and session_id:
            await self.memory.add_message(session_id, "assistant", final_text)

        logger.info("agent_run_complete", agent=agent_name, steps=len(steps), provider=used_provider)
        return AgentRunResult(
            agent=agent_name,
            output=final_text,
            session_id=session_id,
            steps=steps,
            model=used_model,
            provider=used_provider,
        )


def _parse_text_tool_call(content: str) -> tuple[str, dict[str, Any]] | None:
    """Parse mock-friendly tool calls: CALL <name> <json>."""
    text = (content or "").strip()
    # Strip mock prefix if present
    if text.startswith("[mock:"):
        # [mock:model] rest
        closing = text.find("]")
        if closing != -1:
            text = text[closing + 1 :].strip()
    if not text.upper().startswith("CALL "):
        return None
    remainder = text[5:].strip()
    parts = remainder.split(" ", 1)
    if not parts or not parts[0]:
        return None
    name = parts[0].strip()
    raw_args = parts[1].strip() if len(parts) > 1 else "{}"
    try:
        args = json.loads(raw_args) if raw_args else {}
    except json.JSONDecodeError:
        args = {"text": raw_args}
    if not isinstance(args, dict):
        args = {"value": args}
    return name, args
