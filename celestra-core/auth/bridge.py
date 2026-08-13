"""Identity bridge — generic product assertion → Core user JWT.

Canonical assertion claims:
  iss, aud, sub, external_subject, product_user_id, application, iat, exp, jti

Transitional Revenue compatibility (isolated):
  firebase_uid → external_subject
  revenue_user_id → product_user_id
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Protocol

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from auth.repository import AuthRepository
from auth.tokens import create_access_token
from config.applications import DEFAULT_BRIDGE_ISSUERS, require_approved_application
from config.settings import Settings
from shared.exceptions.base import (
    ConfigurationError,
    ForbiddenError,
    UnauthorizedError,
    ValidationAppError,
)
from shared.logging.setup import get_logger

logger = get_logger(__name__)

# Mapping provider equals application id (revenue rows used provider="revenue").
def bridge_provider_for(application: str) -> str:
    return application


class ReplayStore(Protocol):
    async def claim_jti(self, jti: str, *, ttl_seconds: int) -> bool:
        """Return True if jti is new (claimed); False if already seen."""


class InMemoryReplayStore:
    """Process-local replay store for tests / when Redis is unavailable in unit tests."""

    def __init__(self) -> None:
        self._seen: set[str] = set()

    async def claim_jti(self, jti: str, *, ttl_seconds: int) -> bool:
        if jti in self._seen:
            return False
        self._seen.add(jti)
        return True


class RedisReplayStore:
    def __init__(self, redis: Any) -> None:
        self._redis = redis

    async def claim_jti(self, jti: str, *, ttl_seconds: int) -> bool:
        key = self._redis.key(f"bridge:jti:{jti}")
        result = await self._redis.raw.set(key, "1", nx=True, ex=max(ttl_seconds, 1))
        return bool(result)


class BridgeExchangeResult:
    def __init__(
        self,
        *,
        access_token: str,
        expires_in: int,
        celestra_user_id: uuid.UUID,
        application: str,
        provisioned: bool,
    ) -> None:
        self.access_token = access_token
        self.expires_in = expires_in
        self.celestra_user_id = celestra_user_id
        self.application = application
        self.provisioned = provisioned


def _normalize_identity_claims(payload: dict[str, Any]) -> dict[str, str]:
    """Map generic (+ transitional Revenue) claims into a stable identity dict."""
    application = require_approved_application(payload.get("application"))

    external_subject = payload.get("external_subject")
    product_user_id = payload.get("product_user_id")
    legacy = False

    # --- transitional Revenue compatibility (do not expand) ---
    if (not isinstance(external_subject, str) or not external_subject.strip()) and isinstance(
        payload.get("firebase_uid"), str
    ):
        external_subject = payload["firebase_uid"]
        legacy = True
    if (not isinstance(product_user_id, str) or not product_user_id.strip()) and isinstance(
        payload.get("revenue_user_id"), str
    ):
        product_user_id = payload["revenue_user_id"]
        legacy = True
    # --- end transitional ---

    if not isinstance(external_subject, str) or not external_subject.strip():
        raise ValidationAppError(
            "Assertion missing external_subject",
            details={"field": "external_subject"},
        )
    if not isinstance(product_user_id, str) or not product_user_id.strip():
        raise ValidationAppError(
            "Assertion missing product_user_id",
            details={"field": "product_user_id"},
        )

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not isinstance(jti, str) or not jti.strip():
        raise ValidationAppError("Assertion missing jti")
    if not isinstance(sub, str) or not sub.strip():
        raise ValidationAppError("Assertion missing sub")
    if sub.strip() != product_user_id.strip():
        raise UnauthorizedError("Assertion subject mismatch")

    return {
        "application": application,
        "external_subject": external_subject.strip(),
        "product_user_id": product_user_id.strip(),
        "jti": jti.strip(),
        "sub": sub.strip(),
        "legacy_revenue_claims": "1" if legacy else "0",
    }


class IdentityBridgeService:
    """Service-only bridge: verify product assertion → Core JWT."""

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        *,
        replay: ReplayStore,
    ) -> None:
        self.session = session
        self.settings = settings
        self.repo = AuthRepository(session)
        self.replay = replay

    def _require_bridge_config(self) -> None:
        if not self.settings.bridge_assertion_secret:
            raise ConfigurationError(
                "Identity bridge is not configured",
                details={"missing": "CELESTRA_BRIDGE_ASSERTION_SECRET"},
            )

    def _expected_issuer(self, application: str) -> str:
        mapping = self.settings.bridge_issuer_map()
        if application in mapping:
            return mapping[application]
        # Legacy single-issuer setting (historically revenue-ai).
        return self.settings.bridge_issuer

    def verify_assertion(self, assertion: str) -> dict[str, Any]:
        self._require_bridge_config()
        try:
            # Decode without issuer check first so we can bind issuer to application.
            payload = jwt.decode(
                assertion,
                self.settings.bridge_assertion_secret,
                algorithms=["HS256"],
                audience=self.settings.bridge_audience,
                options={
                    "require": ["exp", "iat", "jti", "sub", "iss", "aud"],
                    "verify_iss": False,
                },
                leeway=self.settings.bridge_clock_skew_seconds,
            )
        except jwt.ExpiredSignatureError as exc:
            raise UnauthorizedError("Assertion expired") from exc
        except jwt.InvalidAudienceError as exc:
            raise UnauthorizedError("Invalid assertion audience") from exc
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid assertion") from exc

        identity = _normalize_identity_claims(payload)
        expected_iss = self._expected_issuer(identity["application"])
        actual_iss = payload.get("iss")
        if not isinstance(actual_iss, str) or actual_iss.strip() != expected_iss:
            raise UnauthorizedError("Invalid assertion issuer")

        iat = payload.get("iat")
        if iat is not None:
            if isinstance(iat, datetime):
                iat_ts = iat.timestamp()
            else:
                iat_ts = float(iat)
            now = datetime.now(timezone.utc).timestamp()
            if iat_ts - now > self.settings.bridge_clock_skew_seconds:
                raise UnauthorizedError("Assertion iat is in the future")

        return identity

    async def exchange(self, assertion: str) -> BridgeExchangeResult:
        claims = self.verify_assertion(assertion)
        claimed = await self.replay.claim_jti(
            claims["jti"],
            ttl_seconds=self.settings.bridge_jti_ttl_seconds,
        )
        if not claimed:
            raise UnauthorizedError("Assertion replay detected")

        application = claims["application"]
        external_subject = claims["external_subject"]
        product_user_id = claims["product_user_id"]
        provider = bridge_provider_for(application)

        existing = await self.repo.get_external_identity(
            provider=provider,
            application=application,
            external_subject=external_subject,
        )
        provisioned = False
        if existing is None:
            user = await self._provision(
                application=application,
                external_subject=external_subject,
                product_user_id=product_user_id,
            )
            provisioned = True
        else:
            if existing.external_user_id != product_user_id:
                logger.info(
                    "bridge_mapping_mismatch",
                    operation="exchange",
                    application=application,
                )
                raise ForbiddenError("Identity mapping mismatch")
            user = existing.user
            if user is None:
                user = await self.repo.get_user_by_id(existing.user_id)
            if user is None:
                raise UnauthorizedError("Mapped user not found")
            if not user.is_active or user.deleted_at is not None:
                raise ForbiddenError("User account is disabled")

        expires_in = self.settings.bridge_access_token_expire_seconds
        token_jti = uuid.uuid4().hex
        access = create_access_token(
            subject=user.id,
            secret_key=self.settings.secret_key,
            expires_seconds=expires_in,
            algorithm=self.settings.jwt_algorithm,
            extra_claims={
                "iss": self.settings.bridge_token_issuer,
                "aud": self.settings.bridge_token_audience,
                "jti": token_jti,
                "email": user.email,
                "roles": sorted(user.role_names()),
                "is_superuser": user.is_superuser,
                "application": application,
            },
        )
        logger.info(
            "bridge_exchange_ok",
            operation="exchange",
            application=application,
            provisioned=provisioned,
            user_id=str(user.id),
            legacy_revenue_claims=claims.get("legacy_revenue_claims") == "1",
        )
        return BridgeExchangeResult(
            access_token=access,
            expires_in=expires_in,
            celestra_user_id=user.id,
            application=application,
            provisioned=provisioned,
        )

    async def _provision(
        self,
        *,
        application: str,
        external_subject: str,
        product_user_id: str,
    ) -> User:
        # Synthetic non-PII email — uniqueness only; never a mapping key.
        # Revenue keeps historical digest format for continuity of any tooling.
        if application == "revenue":
            digest = hashlib.sha256(external_subject.encode("utf-8")).hexdigest()[:32]
            email = f"bridge-{digest}@users.revenue.celestra.invalid"
        else:
            digest = hashlib.sha256(
                f"{application}:{external_subject}".encode("utf-8")
            ).hexdigest()[:32]
            email = f"bridge-{digest}@users.{application}.celestra.invalid"

        user = await self.repo.create_bridged_user(
            email=email,
            full_name=None,
            role_names=[self.settings.auth_default_role],
        )
        await self.repo.create_external_identity(
            provider=bridge_provider_for(application),
            application=application,
            external_subject=external_subject,
            external_user_id=product_user_id,
            user=user,
        )
        loaded = await self.repo.get_user_by_id(user.id)
        assert loaded is not None
        return loaded


# Backward-compatible name for tests/docs that imported BRIDGE_PROVIDER.
BRIDGE_PROVIDER = "revenue"
