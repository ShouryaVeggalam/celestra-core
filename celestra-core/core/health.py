"""Platform health / readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config.settings import Settings
from core.dependencies import provide_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app: str
    env: str


class ReadyResponse(BaseModel):
    status: str
    redis: bool
    redis_required: bool = False
    database: str


def _redis_is_required(settings: Settings) -> bool:
    """Redis is required only when a configured backend depends on it."""
    return (
        settings.memory_conversation_backend == "redis"
        or settings.workflow_run_backend == "redis"
    )


async def _check_redis() -> bool:
    try:
        from shared.redis.client import get_redis

        redis = get_redis()
        return bool(await redis.ping())
    except Exception:
        return False


async def _check_database() -> bool:
    try:
        from sqlalchemy import text

        from database.session import async_session_factory

        factory = async_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(provide_settings)) -> HealthResponse:
    """Liveness: is the Core process alive? Does not check Redis/DB/providers."""
    return HealthResponse(status="ok", app=settings.app_name, env=settings.env.value)


@router.get("/ready", response_model=None)
async def ready(settings: Settings = Depends(provide_settings)) -> ReadyResponse | JSONResponse:
    """Readiness: can this instance safely serve traffic?

    Returns HTTP 503 when a *required* dependency is unavailable.
    Optional Redis failure does not mark the instance unready.
    """
    redis_required = _redis_is_required(settings)
    redis_ok = await _check_redis()

    database_status = "skipped"
    database_ok = True
    if settings.ready_check_db:
        database_ok = await _check_database()
        database_status = "ok" if database_ok else "unavailable"

    is_ready = True
    if redis_required and not redis_ok:
        is_ready = False
    if settings.ready_check_db and not database_ok:
        is_ready = False

    body = ReadyResponse(
        status="ok" if is_ready else "unavailable",
        redis=redis_ok,
        redis_required=redis_required,
        database=database_status,
    )
    if not is_ready:
        return JSONResponse(status_code=503, content=body.model_dump())
    return body
