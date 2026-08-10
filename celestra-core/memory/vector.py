"""In-memory vector store with cosine similarity (foundation; swap for pgvector later)."""

from __future__ import annotations

import math

from memory.base import VectorStore
from memory.types import VectorRecord, VectorSearchHit


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._records: dict[str, VectorRecord] = {}

    async def upsert(self, records: list[VectorRecord]) -> None:
        for record in records:
            self._records[record.id] = record.model_copy(deep=True)

    async def search(self, embedding: list[float], *, top_k: int = 5) -> list[VectorSearchHit]:
        scored: list[VectorSearchHit] = []
        for record in self._records.values():
            score = cosine_similarity(embedding, record.embedding)
            scored.append(
                VectorSearchHit(
                    id=record.id,
                    text=record.text,
                    score=score,
                    metadata=record.metadata,
                )
            )
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]

    async def delete(self, record_id: str) -> None:
        self._records.pop(record_id, None)

    def __len__(self) -> int:
        return len(self._records)
