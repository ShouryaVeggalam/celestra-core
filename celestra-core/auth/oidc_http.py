"""OIDC HTTP endpoints — authorize redirect + callback exchange."""

from __future__ import annotations

from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from auth.oidc import OIDCClient, OIDCTokens, OIDCUserInfo
from config.settings import Settings, get_settings
from core.container import Container, get_container
from shared.exceptions.base import ConfigurationError, ValidationAppError

router = APIRouter(prefix="/auth/oidc", tags=["auth-oidc"])


class OIDCAuthorizeResponse(BaseModel):
    authorization_url: str
    state: str


class OIDCCallbackResponse(BaseModel):
    tokens: OIDCTokens
    userinfo: OIDCUserInfo | None = None


def provide_oidc(container: Annotated[Container, Depends(get_container)]) -> OIDCClient:
    try:
        client = container.resolve("oidc_client")
    except KeyError as exc:
        raise ConfigurationError("OIDC is not configured on this deployment") from exc
    assert isinstance(client, OIDCClient)
    return client


@router.get("/authorize", response_model=OIDCAuthorizeResponse)
async def oidc_authorize(
    client: Annotated[OIDCClient, Depends(provide_oidc)],
    state: str | None = None,
) -> OIDCAuthorizeResponse:
    resolved_state = state or uuid4().hex
    url = await client.authorization_url(state=resolved_state, nonce=uuid4().hex)
    return OIDCAuthorizeResponse(authorization_url=url, state=resolved_state)


@router.get("/authorize/redirect")
async def oidc_authorize_redirect(
    client: Annotated[OIDCClient, Depends(provide_oidc)],
    state: str | None = None,
) -> RedirectResponse:
    resolved_state = state or uuid4().hex
    url = await client.authorization_url(state=resolved_state, nonce=uuid4().hex)
    return RedirectResponse(url)


@router.get("/callback", response_model=OIDCCallbackResponse)
async def oidc_callback(
    client: Annotated[OIDCClient, Depends(provide_oidc)],
    code: Annotated[str, Query(min_length=1)],
    state: str | None = None,
    include_userinfo: bool = True,
) -> OIDCCallbackResponse:
    if not code:
        raise ValidationAppError("code is required")
    tokens = await client.exchange_code(code)
    userinfo = None
    if include_userinfo:
        userinfo = await client.userinfo(tokens.access_token)
    return OIDCCallbackResponse(tokens=tokens, userinfo=userinfo)


@router.get("/status")
async def oidc_status(
    settings: Annotated[Settings, Depends(get_settings)],
    container: Annotated[Container, Depends(get_container)],
) -> dict[str, Any]:
    configured = False
    try:
        container.resolve("oidc_client")
        configured = True
    except KeyError:
        configured = False
    return {
        "enabled": bool(settings.oidc_issuer and settings.oidc_client_id),
        "configured": configured,
        "issuer": settings.oidc_issuer,
    }
