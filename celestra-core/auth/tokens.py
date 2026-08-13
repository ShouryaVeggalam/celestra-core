"""JWT access/refresh token issue and verification."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt

from shared.exceptions.base import UnauthorizedError


class TokenError(UnauthorizedError):
    code = "invalid_token"
    message = "Invalid or expired token"


def create_access_token(
    *,
    subject: str | UUID,
    secret_key: str,
    expires_minutes: int = 30,
    expires_seconds: int | None = None,
    algorithm: str = "HS256",
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    if expires_seconds is not None:
        lifetime = timedelta(seconds=expires_seconds)
    else:
        lifetime = timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": "access",
        "iat": now,
        "exp": now + lifetime,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def create_refresh_token(
    *,
    subject: str | UUID,
    secret_key: str,
    expires_days: int = 14,
    algorithm: str = "HS256",
    jti: str | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=expires_days),
    }
    if jti:
        payload["jti"] = jti
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_token(
    token: str,
    *,
    secret_key: str,
    algorithms: list[str] | None = None,
    expected_type: str | None = None,
) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=algorithms or ["HS256"],
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise TokenError("Invalid or expired token") from exc

    if expected_type and payload.get("type") != expected_type:
        raise TokenError(f"Expected {expected_type} token")
    if "sub" not in payload:
        raise TokenError("Token missing subject")
    return payload
