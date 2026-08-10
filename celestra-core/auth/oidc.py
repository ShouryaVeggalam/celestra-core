"""OIDC / OAuth2 helpers for enterprise SSO (authorization-code + token exchange)."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field

from shared.exceptions.base import ConfigurationError, ExternalServiceError, ValidationAppError
from shared.logging.setup import get_logger

logger = get_logger(__name__)


class OIDCSettings(BaseModel):
    issuer: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list[str] = Field(default_factory=lambda: ["openid", "profile", "email"])
    authorize_url: str | None = None
    token_url: str | None = None
    userinfo_url: str | None = None


class OIDCTokens(BaseModel):
    access_token: str
    id_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "Bearer"
    expires_in: int | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class OIDCUserInfo(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None
    preferred_username: str | None = None
    claims: dict[str, Any] = Field(default_factory=dict)


class OIDCClient:
    """Generic OIDC client — works with Auth0, Okta, Keycloak, Azure AD, etc."""

    def __init__(self, settings: OIDCSettings) -> None:
        if not settings.issuer or not settings.client_id:
            raise ConfigurationError("OIDC issuer and client_id are required")
        self.settings = settings
        self._client = httpx.AsyncClient(timeout=30.0)
        self._discovered: dict[str, Any] | None = None

    async def aclose(self) -> None:
        await self._client.aclose()

    async def discover(self) -> dict[str, Any]:
        if self._discovered is not None:
            return self._discovered
        url = self.settings.issuer.rstrip("/") + "/.well-known/openid-configuration"
        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(f"OIDC discovery failed: {exc}") from exc
        self._discovered = resp.json()
        return self._discovered

    async def _endpoint(self, name: str, override: str | None) -> str:
        if override:
            return override
        doc = await self.discover()
        if name not in doc:
            raise ConfigurationError(f"OIDC discovery missing '{name}'")
        return str(doc[name])

    async def authorization_url(self, *, state: str, nonce: str | None = None) -> str:
        authorize = await self._endpoint("authorization_endpoint", self.settings.authorize_url)
        params: dict[str, str] = {
            "response_type": "code",
            "client_id": self.settings.client_id,
            "redirect_uri": self.settings.redirect_uri,
            "scope": " ".join(self.settings.scopes),
            "state": state,
        }
        if nonce:
            params["nonce"] = nonce
        return f"{authorize}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> OIDCTokens:
        if not code:
            raise ValidationAppError("authorization code is required")
        token_url = await self._endpoint("token_endpoint", self.settings.token_url)
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.redirect_uri,
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
        }
        try:
            resp = await self._client.post(token_url, data=data)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(f"OIDC token exchange failed: {exc}") from exc
        payload = resp.json()
        return OIDCTokens(
            access_token=payload["access_token"],
            id_token=payload.get("id_token"),
            refresh_token=payload.get("refresh_token"),
            token_type=payload.get("token_type", "Bearer"),
            expires_in=payload.get("expires_in"),
            raw=payload,
        )

    async def userinfo(self, access_token: str) -> OIDCUserInfo:
        userinfo_url = await self._endpoint("userinfo_endpoint", self.settings.userinfo_url)
        try:
            resp = await self._client.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(f"OIDC userinfo failed: {exc}") from exc
        claims = resp.json()
        return OIDCUserInfo(
            sub=str(claims.get("sub", "")),
            email=claims.get("email"),
            name=claims.get("name"),
            preferred_username=claims.get("preferred_username"),
            claims=claims,
        )
