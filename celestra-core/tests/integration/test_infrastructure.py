"""Placeholder for Redis/DB integration tests (requires docker-compose)."""

import pytest


@pytest.mark.skip(reason="Requires running Redis/Postgres — enable in CI with compose")
def test_redis_ping_placeholder():
    assert False
