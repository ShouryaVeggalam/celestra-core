"""Firebase ID token verification (verify-only; no service account required)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional

import httpx
import jwt
from jwt import PyJWKClient

from app.config import Settings

GOOGLE_CERTS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
_JWKS_URL = "https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com"


class FirebaseAuthError(Exception):
    def __init__(self, message: str = "Invalid Firebase credentials") -> None:
        self.message = message
        super().__init__(message)


@dataclass(frozen=True)
class FirebaseClaims:
    uid: str
    email: Optional[str]
    name: Optional[str]
    email_verified: bool


_jwk_client: Optional[PyJWKClient] = None


def _client() -> PyJWKClient:
    global _jwk_client
    if _jwk_client is None:
        _jwk_client = PyJWKClient(_JWKS_URL, cache_keys=True, lifespan=3600)
    return _jwk_client


def reset_jwk_client() -> None:
    """Test helper to clear cached JWKS client."""
    global _jwk_client
    _jwk_client = None


def verify_firebase_id_token(token: str, settings: Settings) -> FirebaseClaims:
    project_id = (settings.firebase_project_id or "").strip()
    if not project_id:
        raise FirebaseAuthError("Firebase project is not configured.")
    if not token or not token.strip():
        raise FirebaseAuthError("Missing Firebase ID token.")

    try:
        signing_key = _client().get_signing_key_from_jwt(token)
        payload: dict[str, Any] = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=project_id,
            issuer=f"https://securetoken.google.com/{project_id}",
            options={"require": ["exp", "iat", "sub", "aud", "iss"]},
        )
    except FirebaseAuthError:
        raise
    except Exception as exc:  # noqa: BLE001 — map all verify failures to 401
        raise FirebaseAuthError("Invalid or expired Firebase ID token.") from exc

    uid = str(payload.get("sub") or "").strip()
    if not uid or len(uid) > 128:
        raise FirebaseAuthError("Firebase token subject is invalid.")

    # Reject tokens issued too far in the future (clock skew).
    iat = int(payload.get("iat") or 0)
    if iat and iat > int(time.time()) + 300:
        raise FirebaseAuthError("Firebase token is not yet valid.")

    email = payload.get("email")
    name = payload.get("name")
    return FirebaseClaims(
        uid=uid,
        email=str(email).strip() if email else None,
        name=str(name).strip() if name else None,
        email_verified=bool(payload.get("email_verified")),
    )


def fetch_google_certs_reachable(timeout: float = 5.0) -> bool:
    """Operational probe — does not validate tokens."""
    try:
        response = httpx.get(GOOGLE_CERTS_URL, timeout=timeout)
        return response.status_code == 200
    except Exception:  # noqa: BLE001
        return False
