"""
Storage module — object storage for all Celestra applications.

Product apps upload/download via StorageService, not raw S3/local code.
"""

from __future__ import annotations

from typing import Any

from storage.base import ObjectStore
from storage.service import StorageService
from storage.types import ObjectInfo, StoredObject

__all__ = ["ObjectInfo", "ObjectStore", "StorageService", "StoredObject", "storage_router"]


def __getattr__(name: str) -> Any:
    if name == "storage_router":
        from storage.http import router as storage_router

        return storage_router
    raise AttributeError(name)
