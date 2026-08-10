"""Postgres JSONB vector store — durable embeddings without requiring pgvector."""

from __future__ import annotations

import math
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from memory.base import VectorStore
from memory.types import VectorRecord, VectorSearchHit
from database.platform_models import VectorRecordModel


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class PostgresVectorStore(VectorStore):
    """Stores embeddings as JSONB; similarity computed in Python (upgrade to pgvector later)."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        *,
        namespace: str = "default",
    ) -> None:
        self.session_factory = session_factory
        self.namespace = namespace

    async def upsert(self, records: list[VectorRecord]) -> None:
        async with self.session_factory() as session:
            for record in records:
                try:
                    rid = uuid.UUID(record.id)
                except ValueError:
                    rid = uuid.uuid5(uuid.NAMESPACE_URL, record.id)
                existing = await session.get(VectorRecordModel, rid)
                if existing is None:
                    session.add(
                        VectorRecordModel(
                            id=rid,
                            namespace=self.namespace,
                            text=record.text,
                            embedding=list(record.embedding),
                            meta=dict(record.metadata),
                        )
                    )
                else:
                    existing.text = record.text
                    existing.embedding = list(record.embedding)
                    existing.meta = dict(record.metadata)
                    existing.namespace = self.namespace
            await session.commit()

    async def search(self, embedding: list[float], *, top_k: int = 5) -> list[VectorSearchHit]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(VectorRecordModel).where(VectorRecordModel.namespace == self.namespace)
            )
            rows = list(result.scalars().all())
        scored: list[VectorSearchHit] = []
        for row in rows:
            emb = list(row.embedding or [])
            scored.append(
                VectorSearchHit(
                    id=str(row.id),
                    text=row.text,
                    score=_cosine(embedding, emb),
                    metadata=dict(row.meta or {}),
                )
            )
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]

    async def delete(self, record_id: str) -> None:
        async with self.session_factory() as session:
            try:
                rid = uuid.UUID(record_id)
            except ValueError:
                return
            row = await session.get(VectorRecordModel, rid)
            if row is not None:
                await session.delete(row)
                await session.commit()
