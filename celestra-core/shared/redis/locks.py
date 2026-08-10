"""Reusable distributed locking via Redis SET NX EX."""

from __future__ import annotations

import asyncio
import uuid
from types import TracebackType
from typing import Optional, Type

from shared.redis.client import RedisClient


class LockAcquisitionError(RuntimeError):
    """Raised when a distributed lock cannot be acquired."""


_UNLOCK_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
  return redis.call("del", KEYS[1])
else
  return 0
end
"""


class DistributedLock:
    def __init__(
        self,
        redis: RedisClient,
        name: str,
        *,
        ttl: int = 30,
        wait: bool = False,
        wait_timeout: float = 5.0,
        poll_interval: float = 0.1,
    ) -> None:
        self._redis = redis
        self.name = name
        self.ttl = ttl
        self.wait = wait
        self.wait_timeout = wait_timeout
        self.poll_interval = poll_interval
        self._token = str(uuid.uuid4())
        self._held = False

    @property
    def key(self) -> str:
        return self._redis.key(f"lock:{self.name}")

    async def acquire(self) -> bool:
        deadline = asyncio.get_event_loop().time() + self.wait_timeout
        while True:
            acquired = await self._redis.raw.set(self.key, self._token, nx=True, ex=self.ttl)
            if acquired:
                self._held = True
                return True
            if not self.wait:
                return False
            if asyncio.get_event_loop().time() >= deadline:
                return False
            await asyncio.sleep(self.poll_interval)

    async def release(self) -> None:
        if not self._held:
            return
        await self._redis.raw.eval(_UNLOCK_SCRIPT, 1, self.key, self._token)
        self._held = False

    async def __aenter__(self) -> DistributedLock:
        ok = await self.acquire()
        if not ok:
            raise LockAcquisitionError(f"Could not acquire lock '{self.name}'")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.release()
