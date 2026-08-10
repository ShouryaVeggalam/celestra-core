"""Build object store from settings."""

from __future__ import annotations

from pathlib import Path

from config.settings import Settings
from shared.logging.setup import get_logger
from storage.base import ObjectStore
from storage.local import LocalObjectStore
from storage.memory_store import InMemoryObjectStore
from storage.s3 import S3CompatibleObjectStore

logger = get_logger(__name__)


def build_object_store(settings: Settings) -> ObjectStore:
    backend = (settings.storage_backend or "local").lower()
    if backend == "memory":
        return InMemoryObjectStore(default_bucket=settings.storage_bucket)
    if backend == "s3":
        if not settings.s3_endpoint_url or not settings.s3_access_key or not settings.s3_secret_key:
            logger.warning("s3_backend_missing_credentials_falling_back_to_local")
            return LocalObjectStore(settings.storage_local_path, default_bucket=settings.storage_bucket)
        logger.info("storage_backend", backend="s3", endpoint=settings.s3_endpoint_url)
        return S3CompatibleObjectStore(
            endpoint_url=settings.s3_endpoint_url,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            default_bucket=settings.storage_bucket,
            region=settings.s3_region,
        )
    path = Path(settings.storage_local_path)
    logger.info("storage_backend", backend="local", path=str(path))
    return LocalObjectStore(path, default_bucket=settings.storage_bucket)
