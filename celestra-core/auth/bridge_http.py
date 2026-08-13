"""Identity bridge HTTP API — service credential + signed assertion → Core JWT."""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from auth.bridge import IdentityBridgeService, InMemoryReplayStore, RedisReplayStore
from auth.dependencies import get_current_user
from auth.models import User
from config.environment import Environment
from config.settings import Settings, get_settings
from database.session import get_async_session
from monitoring.application_context import bind_application
from monitoring.operations import timed_operation
from shared.exceptions.base import ConfigurationError, UnauthorizedError
from shared.redis.client import get_redis

router = APIRouter(prefix="/auth/bridge", tags=["auth-bridge"])


class BridgeExchangeRequest(BaseModel):
    assertion: str = Field(min_length=16, max_length=8192)


class BridgeExchangeResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    celestra_user_id: UUID
    application: str
    provisioned: bool = False


def _build_replay_store(settings: Settings) -> Any:
    try:
        redis = get_redis()
        return RedisReplayStore(redis)
    except RuntimeError:
        if settings.env is Environment.TEST or settings.debug:
            return InMemoryReplayStore()
        raise ConfigurationError(
            "Identity bridge requires Redis for assertion replay protection",
            details={"backend": "redis"},
        )


@router.post("/exchange", response_model=BridgeExchangeResponse)
async def bridge_exchange(
    payload: BridgeExchangeRequest,
    service_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> BridgeExchangeResponse:
    """Exchange a signed product assertion for a short-lived Core access JWT.

    Requires a **service** credential (typically X-API-Key). The returned JWT's
    ``sub`` is the mapped end-user Core UUID — never the service account.
    """
    # Service principal must authenticate; we do not use service_user as owner.
    if not service_user.is_active:
        raise UnauthorizedError("Service principal inactive")

    if not settings.bridge_assertion_secret:
        raise ConfigurationError(
            "Identity bridge is not configured",
            details={"missing": "CELESTRA_BRIDGE_ASSERTION_SECRET"},
        )

    bridge = IdentityBridgeService(
        session,
        settings,
        replay=_build_replay_store(settings),
    )
    # Privacy: never log assertion, JWTs, or identity secrets.
    async with timed_operation(
        "bridge_exchange",
        result_mapper="bridge",
    ) as op:
        result = await bridge.exchange(payload.assertion)
        bind_application(result.application)
        op.set(provisioned=result.provisioned, application=result.application)
        # Re-bind application on the timer via fields; also update label context.
        await session.commit()

    return BridgeExchangeResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
        celestra_user_id=result.celestra_user_id,
        application=result.application,
        provisioned=result.provisioned,
    )
