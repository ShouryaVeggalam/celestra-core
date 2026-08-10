"""Auth HTTP API — platform identity endpoints for all Celestra apps."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from auth.dependencies import get_auth_service, get_current_user, require_permissions
from auth.models import User
from auth.schemas import (
    ApiKeyCreate,
    ApiKeyCreated,
    ApiKeyRead,
    RefreshRequest,
    TokenPair,
    UserCreate,
    UserLogin,
    UserRead,
)
from auth.service import AuthService
from config.settings import Settings, get_settings
from monitoring.metrics import get_metrics
from shared.exceptions.base import ForbiddenError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserRead:
    if not settings.auth_allow_registration:
        raise ForbiddenError("Registration is disabled")
    return await service.register(payload, default_role=settings.auth_default_role)


@router.post("/login", response_model=TokenPair)
async def login(
    payload: UserLogin,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPair:
    try:
        tokens = await service.login(
            payload,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
        get_metrics().track_login(success=True)
        return tokens
    except Exception:
        get_metrics().track_login(success=False)
        raise


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPair:
    return await service.refresh(
        payload.refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: RefreshRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    await service.logout(payload.refresh_token)


@router.get("/me", response_model=UserRead)
async def me(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserRead:
    return await service.get_me(user.id)


@router.post("/api-keys", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreate,
    user: Annotated[User, Depends(require_permissions("api_keys:manage"))],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> ApiKeyCreated:
    return await service.create_api_key(
        user,
        name=payload.name,
        scopes=payload.scopes,
        expires_in_days=payload.expires_in_days,
    )


@router.get("/api-keys", response_model=list[ApiKeyRead])
async def list_api_keys(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> list[ApiKeyRead]:
    return await service.list_api_keys(user)


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    await service.revoke_api_key(user, key_id)
