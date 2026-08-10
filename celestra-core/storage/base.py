"""Object storage interface — local/S3/gateway adapters implement this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO

from storage.types import ObjectInfo, StoredObject


class ObjectStore(ABC):
    name: str = "object_store"

    @abstractmethod
    async def put(
        self,
        key: str,
        data: bytes | BinaryIO,
        *,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
        bucket: str | None = None,
    ) -> ObjectInfo: ...

    @abstractmethod
    async def get(self, key: str, *, bucket: str | None = None) -> StoredObject: ...

    @abstractmethod
    async def delete(self, key: str, *, bucket: str | None = None) -> None: ...

    @abstractmethod
    async def exists(self, key: str, *, bucket: str | None = None) -> bool: ...

    @abstractmethod
    async def url(self, key: str, *, bucket: str | None = None, expires_in: int = 3600) -> str: ...

    async def list_keys(self, *, prefix: str = "", bucket: str | None = None) -> list[str]:
        raise NotImplementedError
