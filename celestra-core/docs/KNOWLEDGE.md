# Knowledge — Celestra Core (Phase 5)

Document ingestion + RAG over the AI facade.

## Capabilities

- Knowledge bases
- Text chunking + embedding
- Optional persistence of raw docs to Storage
- Grounded `query()` with source citations

## Usage

```python
from knowledge import KnowledgeService, IngestTextRequest, QueryRequest

knowledge.create_knowledge_base("hiring-policies")
await knowledge.ingest_text(
    IngestTextRequest(
        knowledge_base="hiring-policies",
        title="Interview rubric",
        content="...",
    )
)
answer = await knowledge.query(
    QueryRequest(knowledge_base="hiring-policies", question="How do we score system design?")
)
```

## HTTP (`/api/v1/knowledge`) — auth required

| Method | Path |
|---|---|
| POST | `/bases` |
| GET | `/bases` |
| POST | `/ingest` |
| POST | `/query` |
| GET | `/bases/{name}/documents` |
