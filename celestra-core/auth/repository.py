"""Auth persistence — repository layer over SQLAlchemy async sessions."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.models import ApiKey, Permission, RefreshToken, Role, User
from auth.passwords import hash_password
from shared.utils.dates import utcnow


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .where(User.email == email.lower(), User.deleted_at.is_(None))
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None = None,
        role_names: list[str] | None = None,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            email=email.lower(),
            hashed_password=hash_password(password),
            full_name=full_name,
            is_superuser=is_superuser,
        )
        if role_names:
            roles = await self.get_roles_by_names(role_names)
            user.roles = roles
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_roles_by_names(self, names: list[str]) -> list[Role]:
        stmt = (
            select(Role)
            .where(Role.name.in_(names))
            .options(selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_or_create_role(self, name: str, description: str | None = None) -> Role:
        stmt = select(Role).where(Role.name == name).options(selectinload(Role.permissions))
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()
        if role:
            return role
        role = Role(name=name, description=description)
        self.session.add(role)
        await self.session.flush()
        return role

    async def get_or_create_permission(self, code: str, description: str | None = None) -> Permission:
        stmt = select(Permission).where(Permission.code == code)
        result = await self.session.execute(stmt)
        perm = result.scalar_one_or_none()
        if perm:
            return perm
        perm = Permission(code=code, description=description)
        self.session.add(perm)
        await self.session.flush()
        return perm

    async def touch_last_login(self, user: User) -> None:
        user.last_login_at = utcnow()
        await self.session.flush()

    async def store_refresh_token(
        self,
        *,
        user: User,
        jti: str,
        raw_token: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> RefreshToken:
        record = RefreshToken(
            user_id=user.id,
            jti=jti,
            token_hash=_hash_token(raw_token),
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_refresh_token(self, jti: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token: RefreshToken) -> None:
        token.revoked_at = utcnow()
        await self.session.flush()

    async def revoke_all_refresh_tokens(self, user_id: uuid.UUID) -> None:
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        result = await self.session.execute(stmt)
        now = utcnow()
        for token in result.scalars().all():
            token.revoked_at = now
        await self.session.flush()

    async def create_api_key(
        self,
        *,
        user: User,
        name: str,
        scopes: list[str] | None = None,
        expires_in_days: int | None = None,
    ) -> tuple[ApiKey, str]:
        raw = f"cel_{secrets.token_urlsafe(32)}"
        prefix = raw[:12]
        expires_at = None
        if expires_in_days:
            expires_at = utcnow() + timedelta(days=expires_in_days)
        key = ApiKey(
            user_id=user.id,
            name=name,
            key_prefix=prefix,
            key_hash=_hash_token(raw),
            scopes=",".join(scopes or []),
            expires_at=expires_at,
        )
        self.session.add(key)
        await self.session.flush()
        return key, raw

    async def list_api_keys(self, user_id: uuid.UUID) -> list[ApiKey]:
        stmt = select(ApiKey).where(ApiKey.user_id == user_id).order_by(ApiKey.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_api_key(self, key_id: uuid.UUID, user_id: uuid.UUID) -> ApiKey | None:
        stmt = select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_api_key_by_raw(self, raw_key: str) -> ApiKey | None:
        prefix = raw_key[:12]
        stmt = (
            select(ApiKey)
            .where(ApiKey.key_prefix == prefix, ApiKey.revoked_at.is_(None))
            .options(selectinload(ApiKey.user).selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        for key in result.scalars().all():
            if key.key_hash == _hash_token(raw_key):
                return key
        return None

    async def revoke_api_key(self, key: ApiKey) -> None:
        key.revoked_at = utcnow()
        await self.session.flush()

    async def touch_api_key(self, key: ApiKey) -> None:
        key.last_used_at = utcnow()
        await self.session.flush()
