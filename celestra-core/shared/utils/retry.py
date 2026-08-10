"""Retry helpers built on tenacity — sync and async."""

from __future__ import annotations

from typing import Callable, TypeVar

from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

T = TypeVar("T")


def retry_sync(
    fn: Callable[[], T],
    *,
    attempts: int = 3,
    min_wait: float = 0.2,
    max_wait: float = 2.0,
    retry_on: type[BaseException] | tuple[type[BaseException], ...] = Exception,
) -> T:
    retrying = Retrying(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=min_wait, max=max_wait),
        retry=retry_if_exception_type(retry_on),
        reraise=True,
    )
    return retrying(fn)


async def retry_async(
    fn: Callable[[], T],
    *,
    attempts: int = 3,
    min_wait: float = 0.2,
    max_wait: float = 2.0,
    retry_on: type[BaseException] | tuple[type[BaseException], ...] = Exception,
) -> T:
    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=min_wait, max=max_wait),
        retry=retry_if_exception_type(retry_on),
        reraise=True,
    ):
        with attempt:
            result = fn()
            if hasattr(result, "__await__"):
                return await result  # type: ignore[misc]
            return result  # type: ignore[return-value]
    raise RuntimeError("retry_async exhausted without result")  # pragma: no cover
