"""Auth domain models — identity, RBAC, API keys, refresh tokens."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


user_roles = Table(
    "auth_user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("auth_users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("auth_roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "auth_role_permissions",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("auth_roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("auth_permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Platform user identity."""

    __tablename__ = "auth_users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )
    api_keys: Mapped[list[ApiKey]] = relationship("ApiKey", back_populates="user", lazy="selectin")
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken",
        back_populates="user",
        lazy="noload",
    )

    def permission_codes(self) -> set[str]:
        codes: set[str] = set()
        for role in self.roles:
            for perm in role.permissions:
                codes.add(perm.code)
        return codes

    def role_names(self) -> set[str]:
        return {role.name for role in self.roles}


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Named role used for RBAC."""

    __tablename__ = "auth_roles"
    __table_args__ = (UniqueConstraint("name", name="uq_auth_roles_name"),)

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    users: Mapped[list[User]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        lazy="noload",
    )
    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )


class Permission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Fine-grained permission code (e.g. users:read)."""

    __tablename__ = "auth_permissions"
    __table_args__ = (UniqueConstraint("code", name="uq_auth_permissions_code"),)

    code: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="noload",
    )


class ApiKey(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Machine credential for service-to-service / SDK access."""

    __tablename__ = "auth_api_keys"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    scopes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # comma-separated
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="api_keys")

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None


class RefreshToken(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Persisted refresh token (hashed) for rotation / revocation."""

    __tablename__ = "auth_refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jti: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None
