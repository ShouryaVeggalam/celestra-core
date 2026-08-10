"""FastAPI auth dependencies — JWT bearer + API key + RBAC guards."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from auth.rbac import assert_permissions, assert_roles
from auth.repository import AuthRepository
from auth.service import AuthService
from auth.tokens import decode_token
from config.settings import Settings, get_settings
from database.session import get_async_session
from shared.exceptions.base import UnauthorizedError
from shared.logging.context import bind_context

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthService:
    return AuthService(session, settings)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    session: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings),
) -> User:
    """
    Resolve the current principal.

    Supports:
    - Authorization: Bearer <access_jwt>
    - X-API-Key: cel_...
    """
    service = AuthService(session, settings)

    if x_api_key:
        user = await service.authenticate_api_key(x_api_key)
        bind_context(user_id=str(user.id), auth_method="api_key")
        request.state.user = user
        return user

    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Authentication required")

    payload = decode_token(
        credentials.credentials,
        secret_key=settings.secret_key,
        algorithms=[settings.jwt_algorithm],
        expected_type="access",
    )
    user = await AuthRepository(session).get_user_by_id(uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    bind_context(user_id=str(user.id), auth_method="jwt")
    request.state.user = user
    return user


async def get_optional_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    session: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings),
) -> User | None:
    if credentials is None and not x_api_key:
        return None
    try:
        return await get_current_user(request, credentials, x_api_key, session, settings)
    except UnauthorizedError:
        return None


def require_roles(*roles: str) -> Callable:
    async def _dependency(user: User = Depends(get_current_user)) -> User:
        assert_roles(user, *roles)
        return user

    return _dependency


def require_permissions(*permissions: str, require_all: bool = False) -> Callable:
    async def _dependency(user: User = Depends(get_current_user)) -> User:
        assert_permissions(user, *permissions, require_all=require_all)
        return user

    return _dependency
