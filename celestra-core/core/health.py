"""Platform health / readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from config.settings import Settings
from core.dependencies import provide_redis, provide_settings
from shared.redis.client import RedisClient

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app: str
    env: str


class ReadyResponse(BaseModel):
    status: str
    redis: bool
    database: str


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(provide_settings)) -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name, env=settings.env.value)


@router.get("/ready", response_model=ReadyResponse)
async def ready(
    settings: Settings = Depends(provide_settings),
    redis: RedisClient = Depends(provide_redis),
) -> ReadyResponse:
    redis_ok = False
    try:
        redis_ok = await redis.ping()
    except Exception:
        redis_ok = False
    return ReadyResponse(
        status="ok" if redis_ok else "degraded",
        redis=redis_ok,
        database="configured",
    )
