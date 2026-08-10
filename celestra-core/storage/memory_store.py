"""In-memory object store for tests."""

from __future__ import annotations

import hashlib
from typing import BinaryIO

from shared.exceptions.base import NotFoundError
from shared.utils.dates import utcnow
from storage.base import ObjectStore
from storage.types import ObjectInfo, StoredObject


class InMemoryObjectStore(ObjectStore):
    name = "memory"

    def __init__(self, *, default_bucket: str = "default") -> None:
        self.default_bucket = default_bucket
        self._objects: dict[tuple[str, str], StoredObject] = {}

    def _key(self, key: str, bucket: str | None) -> tuple[str, str]:
        return (bucket or self.default_bucket, key)

    async def put(
        self,
        key: str,
        data: bytes | BinaryIO,
        *,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
        bucket: str | None = None,
    ) -> ObjectInfo:
        raw = data.read() if hasattr(data, "read") else data  # type: ignore[union-attr]
        assert isinstance(raw, (bytes, bytearray))
        info = ObjectInfo(
            key=key,
            bucket=bucket or self.default_bucket,
            size=len(raw),
            content_type=content_type,
            etag=hashlib.md5(raw).hexdigest(),
            metadata=metadata or {},
            created_at=utcnow(),
            url=await self.url(key, bucket=bucket),
        )
        self._objects[self._key(key, bucket)] = StoredObject(info=info, data=bytes(raw))
        return info

    async def get(self, key: str, *, bucket: str | None = None) -> StoredObject:
        obj = self._objects.get(self._key(key, bucket))
        if obj is None:
            raise NotFoundError(f"Object not found: {key}")
        return obj.model_copy(deep=True)

    async def delete(self, key: str, *, bucket: str | None = None) -> None:
        self._objects.pop(self._key(key, bucket), None)

    async def exists(self, key: str, *, bucket: str | None = None) -> bool:
        return self._key(key, bucket) in self._objects

    async def url(self, key: str, *, bucket: str | None = None, expires_in: int = 3600) -> str:
        return f"memory://{(bucket or self.default_bucket)}/{key}?expires_in={expires_in}"

    async def list_keys(self, *, prefix: str = "", bucket: str | None = None) -> list[str]:
        b = bucket or self.default_bucket
        return sorted(k for (bk, k) in self._objects if bk == b and k.startswith(prefix))
