"""UUID helpers."""

from __future__ import annotations

import uuid


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


def is_uuid(value: str | uuid.UUID) -> bool:
    if isinstance(value, uuid.UUID):
        return True
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError, TypeError):
        return False
