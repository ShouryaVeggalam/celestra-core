# Workflows — Celestra Core (Phase 4)

Sequential workflow engine (Temporal-lite) with Celery foundation wiring.

## Capabilities

- Declarative workflows + named step handlers
- In-process durable-style run store
- Demo workflow `demo.greeting`
- Celery task stub `workflows.run` (enable with `CELESTRA_WORKFLOW_CELERY_ENABLED=true`)

## Usage

```python
from workflows import WorkflowService, StartWorkflowRequest

run = await workflows.start(StartWorkflowRequest(workflow="demo.greeting", input={"name": "Ada"}))
assert run.status.value == "completed"
```

## HTTP (`/api/v1/workflows`) — auth required

| Method | Path | Description |
|---|---|---|
| GET | `/` | List definitions |
| POST | `/start` | Start a run |
| GET | `/runs` | List runs |
| GET | `/runs/{id}` | Get run |

## Built-in steps

`set_value`, `merge`, `format_message`, `uppercase`

## Celery worker (optional)

```bash
celery -A workflows.celery_app.celery_app worker -l info
```

In-process execution is the default until a shared Redis/DB run store lands.
