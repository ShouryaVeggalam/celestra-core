"""
S3-compatible object store via HTTP (MinIO / gateway).

Uses path-style URLs and static access headers. For production AWS signing,
swap this adapter for a boto3-backed implementation without changing callers.
"""

from __future__ import annotations

import hashlib
from typing import BinaryIO
from urllib.parse import quote

import httpx

from shared.exceptions.base import ExternalServiceError, NotFoundError
from shared.utils.dates import utcnow
from storage.base import ObjectStore
from storage.types import ObjectInfo, StoredObject


class S3CompatibleObjectStore(ObjectStore):
    name = "s3"

    def __init__(
        self,
        *,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        default_bucket: str = "celestra",
        region: str = "us-east-1",
        timeout: float = 30.0,
    ) -> None:
        self.endpoint_url = endpoint_url.rstrip("/")
        self.access_key = access_key
        self.secret_key = secret_key
        self.default_bucket = default_bucket
        self.region = region
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                # Gateway-friendly auth; MinIO also accepts these via reverse proxies
                "X-Access-Key": access_key,
                "X-Secret-Key": secret_key,
            },
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    def _url(self, bucket: str, key: str) -> str:
        return f"{self.endpoint_url}/{bucket}/{quote(key)}"

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
        b = bucket or self.default_bucket
        headers = {"Content-Type": content_type}
        for mk, mv in (metadata or {}).items():
            headers[f"x-amz-meta-{mk}"] = mv
        response = await self._client.put(self._url(b, key), content=bytes(raw), headers=headers)
        if response.status_code >= 400:
            raise ExternalServiceError(
                f"S3 put failed: {response.status_code}",
                details={"body": response.text[:500]},
            )
        return ObjectInfo(
            key=key,
            bucket=b,
            size=len(raw),
            content_type=content_type,
            etag=hashlib.md5(raw).hexdigest(),
            metadata=metadata or {},
            created_at=utcnow(),
            url=await self.url(key, bucket=b),
        )

    async def get(self, key: str, *, bucket: str | None = None) -> StoredObject:
        b = bucket or self.default_bucket
        response = await self._client.get(self._url(b, key))
        if response.status_code == 404:
            raise NotFoundError(f"Object not found: {key}")
        if response.status_code >= 400:
            raise ExternalServiceError(f"S3 get failed: {response.status_code}")
        data = response.content
        return StoredObject(
            info=ObjectInfo(
                key=key,
                bucket=b,
                size=len(data),
                content_type=response.headers.get("content-type", "application/octet-stream"),
                etag=hashlib.md5(data).hexdigest(),
                url=await self.url(key, bucket=b),
            ),
            data=data,
        )

    async def delete(self, key: str, *, bucket: str | None = None) -> None:
        b = bucket or self.default_bucket
        response = await self._client.delete(self._url(b, key))
        if response.status_code not in {200, 204, 404}:
            raise ExternalServiceError(f"S3 delete failed: {response.status_code}")

    async def exists(self, key: str, *, bucket: str | None = None) -> bool:
        b = bucket or self.default_bucket
        response = await self._client.head(self._url(b, key))
        return response.status_code == 200

    async def url(self, key: str, *, bucket: str | None = None, expires_in: int = 3600) -> str:
        b = bucket or self.default_bucket
        return f"{self._url(b, key)}?expires_in={expires_in}"
