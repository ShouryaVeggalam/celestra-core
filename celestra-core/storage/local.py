"""Local filesystem object store — default for development."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO

from shared.exceptions.base import NotFoundError
from shared.utils.dates import utcnow
from storage.base import ObjectStore
from storage.types import ObjectInfo, StoredObject


class LocalObjectStore(ObjectStore):
    name = "local"

    def __init__(self, root: str | Path, *, default_bucket: str = "default") -> None:
        self.root = Path(root)
        self.default_bucket = default_bucket
        self.root.mkdir(parents=True, exist_ok=True)

    def _bucket_dir(self, bucket: str | None) -> Path:
        path = self.root / (bucket or self.default_bucket)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _object_path(self, key: str, bucket: str | None) -> Path:
        # Prevent path traversal
        safe = key.lstrip("/").replace("..", "_")
        return self._bucket_dir(bucket) / safe

    def _meta_path(self, key: str, bucket: str | None) -> Path:
        return Path(str(self._object_path(key, bucket)) + ".meta.json")

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
        path = self._object_path(key, bucket)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(bytes(raw))
        etag = hashlib.md5(raw).hexdigest()
        info = ObjectInfo(
            key=key,
            bucket=bucket or self.default_bucket,
            size=len(raw),
            content_type=content_type,
            etag=etag,
            metadata=metadata or {},
            created_at=utcnow(),
            url=await self.url(key, bucket=bucket),
        )
        self._meta_path(key, bucket).write_text(info.model_dump_json(), encoding="utf-8")
        return info

    async def get(self, key: str, *, bucket: str | None = None) -> StoredObject:
        path = self._object_path(key, bucket)
        if not path.is_file():
            raise NotFoundError(f"Object not found: {key}")
        data = path.read_bytes()
        meta_file = self._meta_path(key, bucket)
        if meta_file.is_file():
            info = ObjectInfo.model_validate_json(meta_file.read_text(encoding="utf-8"))
        else:
            info = ObjectInfo(
                key=key,
                bucket=bucket or self.default_bucket,
                size=len(data),
                url=await self.url(key, bucket=bucket),
            )
        return StoredObject(info=info, data=data)

    async def delete(self, key: str, *, bucket: str | None = None) -> None:
        path = self._object_path(key, bucket)
        meta = self._meta_path(key, bucket)
        if path.exists():
            path.unlink()
        if meta.exists():
            meta.unlink()

    async def exists(self, key: str, *, bucket: str | None = None) -> bool:
        return self._object_path(key, bucket).is_file()

    async def url(self, key: str, *, bucket: str | None = None, expires_in: int = 3600) -> str:
        # Local "signed" path reference for apps; not an HTTP URL
        return f"file://{(bucket or self.default_bucket)}/{key}?expires_in={expires_in}"

    async def list_keys(self, *, prefix: str = "", bucket: str | None = None) -> list[str]:
        base = self._bucket_dir(bucket)
        keys: list[str] = []
        for path in base.rglob("*"):
            if path.is_file() and not path.name.endswith(".meta.json"):
                rel = str(path.relative_to(base))
                if rel.startswith(prefix):
                    keys.append(rel)
        return sorted(keys)
