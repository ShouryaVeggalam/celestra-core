"""Storage facade for product applications."""

from __future__ import annotations

from typing import BinaryIO

from storage.base import ObjectStore
from storage.types import ObjectInfo, StoredObject


class StorageService:
    def __init__(self, store: ObjectStore) -> None:
        self.store = store

    async def upload(
        self,
        key: str,
        data: bytes | BinaryIO,
        *,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
        bucket: str | None = None,
    ) -> ObjectInfo:
        return await self.store.put(
            key, data, content_type=content_type, metadata=metadata, bucket=bucket
        )

    async def download(self, key: str, *, bucket: str | None = None) -> StoredObject:
        return await self.store.get(key, bucket=bucket)

    async def delete(self, key: str, *, bucket: str | None = None) -> None:
        await self.store.delete(key, bucket=bucket)

    async def exists(self, key: str, *, bucket: str | None = None) -> bool:
        return await self.store.exists(key, bucket=bucket)

    async def signed_url(self, key: str, *, bucket: str | None = None, expires_in: int = 3600) -> str:
        return await self.store.url(key, bucket=bucket, expires_in=expires_in)

    async def list_keys(self, *, prefix: str = "", bucket: str | None = None) -> list[str]:
        return await self.store.list_keys(prefix=prefix, bucket=bucket)
