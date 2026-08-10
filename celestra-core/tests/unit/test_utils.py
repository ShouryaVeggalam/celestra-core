"""Unit tests — shared utilities."""

from datetime import timezone

import pytest

from shared.exceptions.base import NotFoundError, ValidationAppError
from shared.utils.dates import parse_iso, to_iso, utcnow
from shared.utils.ids import is_uuid, new_uuid
from shared.utils.pagination import PageParams, paginate_sequence
from shared.utils.serialization import from_json, to_json
from shared.utils.validation import clamp, require_non_empty


def test_uuid_helpers():
    u = new_uuid()
    assert is_uuid(u)
    assert is_uuid(str(u))
    assert not is_uuid("not-a-uuid")


def test_dates_roundtrip():
    now = utcnow()
    assert now.tzinfo == timezone.utc
    iso = to_iso(now)
    parsed = parse_iso(iso)
    assert abs((parsed - now).total_seconds()) < 1


def test_pagination():
    items = list(range(25))
    page = paginate_sequence(items, PageParams(page=2, page_size=10))
    assert page.items == list(range(10, 20))
    assert page.total == 25
    assert page.pages == 3


def test_validation_helpers():
    assert require_non_empty("  hi  ", "name") == "hi"
    with pytest.raises(ValidationAppError):
        require_non_empty("  ", "name")
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0


def test_serialization():
    payload = {"a": 1, "b": "x"}
    assert from_json(to_json(payload)) == payload


def test_exception_to_dict():
    err = NotFoundError("User missing", details={"id": "123"})
    body = err.to_dict()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["details"]["id"] == "123"
