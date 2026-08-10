# Memory — Celestra Core (Phase 4)

Conversation history and semantic recall for every Celestra app.

## Capabilities

- Conversation sessions with windowing
- Semantic `remember` / `recall` via AI embeddings (mock works offline)
- In-memory stores now; Redis/pgvector adapters later

## Usage

```python
from memory import MemoryService

session = await memory.start_session(session_id="s1")
await memory.add_message("s1", "user", "Hello")
await memory.remember_text("Celestra is an AI platform")
hits = await memory.recall("AI platform")
```

## HTTP (`/api/v1/memory`) — auth required

| Method | Path | Description |
|---|---|---|
| POST | `/sessions` | Start/get session |
| POST | `/messages` | Append message |
| GET | `/sessions/{id}/messages` | Windowed history |
| POST | `/remember` | Upsert semantic memory |
| POST | `/recall` | Similarity search |
