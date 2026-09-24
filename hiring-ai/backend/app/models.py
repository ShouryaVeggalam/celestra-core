"""SQLAlchemy models for Hiring AI auth, orgs, and invites."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid.uuid4())


class Status(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    REMOVED = "removed"


class Role(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class InviteCodeRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[Optional[str]] = mapped_column(String(320))
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Status] = mapped_column(
        Enum(Status, native_enum=False, values_callable=lambda e: [i.value for i in e]),
        default=Status.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    memberships: Mapped[list["Membership"]] = relationship(back_populates="user")
    identities: Mapped[list["AuthIdentity"]] = relationship(back_populates="user")


class AuthIdentity(Base):
    """Maps an external auth subject (e.g. Firebase UID) to a User.

    Firebase UIDs are never exposed on User or recruiter API payloads.
    """

    __tablename__ = "auth_identities"
    __table_args__ = (UniqueConstraint("provider", "subject", name="uq_auth_identities_provider_subject"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="identities")


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[Status] = mapped_column(
        Enum(Status, native_enum=False, values_callable=lambda e: [i.value for i in e]),
        default=Status.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    memberships: Mapped[list["Membership"]] = relationship(back_populates="organization")


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("org_id", "user_id", name="uq_memberships_org_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    org_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[Role] = mapped_column(
        Enum(Role, native_enum=False, values_callable=lambda e: [i.value for i in e]),
        default=Role.MEMBER,
        nullable=False,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus, native_enum=False, values_callable=lambda e: [i.value for i in e]),
        default=MembershipStatus.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="memberships")
    organization: Mapped[Organization] = relationship(back_populates="memberships")


class InviteCode(Base):
    """One-time organization invite. Raw code is never stored."""

    __tablename__ = "invite_codes"
    __table_args__ = (UniqueConstraint("code_hash", name="uq_invite_codes_code_hash"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    org_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[InviteCodeRole] = mapped_column(
        Enum(InviteCodeRole, native_enum=False, values_callable=lambda e: [i.value for i in e]),
        default=InviteCodeRole.MEMBER,
        nullable=False,
    )
    created_by_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    used_by_user_id: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class HiringEvent(Base):
    __tablename__ = "hiring_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    org_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor: Mapped[str] = mapped_column(String(32), nullable=False, default="user")
    actor_id: Mapped[Optional[str]] = mapped_column(String(36))
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
