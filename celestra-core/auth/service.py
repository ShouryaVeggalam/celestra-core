"""Auth application service — register, login, tokens, API keys."""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import ApiKey, User
from auth.passwords import verify_password
from auth.repository import AuthRepository
from auth.schemas import (
    ApiKeyCreated,
    ApiKeyRead,
    TokenPair,
    UserCreate,
    UserLogin,
    UserRead,
)
from auth.tokens import create_access_token, create_refresh_token, decode_token
from config.settings import Settings
from shared.exceptions.base import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from shared.utils.dates import utcnow


def user_to_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=sorted(user.role_names()),
        permissions=sorted(user.permission_codes()),
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.repo = AuthRepository(session)

    async def register(self, payload: UserCreate, *, default_role: str = "member") -> UserRead:
        existing = await self.repo.get_user_by_email(payload.email)
        if existing:
            raise ConflictError("Email already registered", details={"email": payload.email})
        user = await self.repo.create_user(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            role_names=[default_role],
        )
        await self.session.refresh(user, attribute_names=["roles"])
        # ensure permissions loaded
        loaded = await self.repo.get_user_by_id(user.id)
        assert loaded is not None
        return user_to_read(loaded)

    async def login(
        self,
        payload: UserLogin,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenPair:
        user = await self.repo.get_user_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise ForbiddenError("User account is disabled")
        await self.repo.touch_last_login(user)
        return await self._issue_token_pair(user, user_agent=user_agent, ip_address=ip_address)

    async def refresh(
        self,
        refresh_token: str,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenPair:
        payload = decode_token(
            refresh_token,
            secret_key=self.settings.secret_key,
            algorithms=[self.settings.jwt_algorithm],
            expected_type="refresh",
        )
        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedError("Refresh token missing jti")
        stored = await self.repo.get_refresh_token(jti)
        if stored is None or stored.is_revoked:
            raise UnauthorizedError("Refresh token revoked or unknown")
        if stored.expires_at < utcnow():
            raise UnauthorizedError("Refresh token expired")

        user = await self.repo.get_user_by_id(uuid.UUID(payload["sub"]))
        if user is None or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        # Rotate: revoke old, issue new
        await self.repo.revoke_refresh_token(stored)
        return await self._issue_token_pair(user, user_agent=user_agent, ip_address=ip_address)

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(
                refresh_token,
                secret_key=self.settings.secret_key,
                algorithms=[self.settings.jwt_algorithm],
                expected_type="refresh",
            )
        except UnauthorizedError:
            return
        jti = payload.get("jti")
        if not jti:
            return
        stored = await self.repo.get_refresh_token(jti)
        if stored and not stored.is_revoked:
            await self.repo.revoke_refresh_token(stored)

    async def get_me(self, user_id: uuid.UUID) -> UserRead:
        user = await self.repo.get_user_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user_to_read(user)

    async def create_api_key(
        self,
        user: User,
        *,
        name: str,
        scopes: list[str] | None = None,
        expires_in_days: int | None = None,
    ) -> ApiKeyCreated:
        key, raw = await self.repo.create_api_key(
            user=user,
            name=name,
            scopes=scopes,
            expires_in_days=expires_in_days,
        )
        return ApiKeyCreated(
            id=key.id,
            name=key.name,
            key=raw,
            key_prefix=key.key_prefix,
            scopes=scopes or [],
            expires_at=key.expires_at,
            created_at=key.created_at,
        )

    async def list_api_keys(self, user: User) -> list[ApiKeyRead]:
        keys = await self.repo.list_api_keys(user.id)
        return [self._api_key_to_read(k) for k in keys]

    async def revoke_api_key(self, user: User, key_id: uuid.UUID) -> None:
        key = await self.repo.get_api_key(key_id, user.id)
        if key is None:
            raise NotFoundError("API key not found")
        await self.repo.revoke_api_key(key)

    async def authenticate_api_key(self, raw_key: str) -> User:
        key = await self.repo.find_api_key_by_raw(raw_key)
        if key is None:
            raise UnauthorizedError("Invalid API key")
        if key.expires_at and key.expires_at < utcnow():
            raise UnauthorizedError("API key expired")
        if key.user is None or not key.user.is_active or key.user.deleted_at is not None:
            raise UnauthorizedError("API key owner inactive")
        await self.repo.touch_api_key(key)
        return key.user

    async def _issue_token_pair(
        self,
        user: User,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenPair:
        jti = uuid.uuid4().hex
        access = create_access_token(
            subject=user.id,
            secret_key=self.settings.secret_key,
            expires_minutes=self.settings.jwt_access_token_expire_minutes,
            algorithm=self.settings.jwt_algorithm,
            extra_claims={
                "email": user.email,
                "roles": sorted(user.role_names()),
                "is_superuser": user.is_superuser,
            },
        )
        refresh = create_refresh_token(
            subject=user.id,
            secret_key=self.settings.secret_key,
            expires_days=self.settings.jwt_refresh_token_expire_days,
            algorithm=self.settings.jwt_algorithm,
            jti=jti,
        )
        await self.repo.store_refresh_token(
            user=user,
            jti=jti,
            raw_token=refresh,
            expires_at=utcnow() + timedelta(days=self.settings.jwt_refresh_token_expire_days),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=self.settings.jwt_access_token_expire_minutes * 60,
        )

    @staticmethod
    def _api_key_to_read(key: ApiKey) -> ApiKeyRead:
        scopes = [s for s in (key.scopes or "").split(",") if s]
        return ApiKeyRead(
            id=key.id,
            name=key.name,
            key_prefix=key.key_prefix,
            scopes=scopes,
            expires_at=key.expires_at,
            last_used_at=key.last_used_at,
            revoked_at=key.revoked_at,
            created_at=key.created_at,
        )
