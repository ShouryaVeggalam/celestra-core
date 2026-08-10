# Agents — Celestra Core (Phase 4)

Tool registry + agent runtime on top of `AIService` and memory.

## Capabilities

- `@registry.tool` registration
- Built-in tools: `echo`, `current_time`, `add`
- Multi-step tool loop (`max_steps`)
- Session memory integration
- Mock-friendly tool syntax: `CALL <tool> <json>`

## Usage

```python
from agents import AgentService, AgentRunRequest, AgentSpec

agent_service.register_agent(AgentSpec(name="recruiter", tools=["echo"]))
result = await agent_service.run(
    AgentRunRequest(agent="assistant", input='CALL echo {"text": "hi"}', session_id="s1")
)
```

## HTTP (`/api/v1/agents`) — auth required

| Method | Path | Description |
|---|---|---|
| GET | `/` | List agents |
| GET | `/tools` | List tools |
| POST | `/run` | Run an agent |

## Default agents

| Name | Tools |
|---|---|
| `assistant` | echo, current_time, add |
| `echo_agent` | echo |
