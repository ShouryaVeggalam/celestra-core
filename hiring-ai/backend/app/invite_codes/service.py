"""Email-less invite codes for multi-user organization access."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.invite_codes.crypto import generate_invite_code, hash_invite_code, normalize_invite_code
from app.invite_codes.errors import InviteCodeError
from app.invite_codes.schemas import (
    CreateInviteCodeRequest,
    InviteCodeCreatedResponse,
    InviteCodeListItem,
    InviteCodeListResponse,
    RedeemInviteCodeRequest,
    RedeemInviteCodeResponse,
)
from app.models import (
    HiringEvent,
    InviteCode,
    InviteCodeRole,
    Membership,
    MembershipStatus,
    Organization,
    Role,
    Status,
    User,
    new_id,
    utcnow,
)

INVITE_TTL_DAYS = 7

ERROR_HTTP = {
    "invite_not_found": 404,
    "invite_expired": 410,
    "invite_used": 409,
    "organization_mismatch": 403,
    "forbidden": 403,
    "organization_not_found": 404,
}


def _enum_value(value: Any) -> Optional[str]:
    if value is None:
        return None
    return value.value if hasattr(value, "value") else str(value)


def _audit(
    db: Session,
    *,
    org_id: str,
    entity_type: str,
    entity_id: str,
    event_type: str,
    actor_id: str,
    payload: dict[str, Any],
) -> None:
    db.add(
        HiringEvent(
            org_id=org_id,
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            actor="user",
            actor_id=actor_id,
            payload=payload,
        )
    )


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _invite_status(row: InviteCode, *, now: datetime) -> str:
    if row.used_at is not None:
        return "used"
    if _aware(row.expires_at) <= now:
        return "expired"
    return "active"


class InviteCodeService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self._db = db
        self._settings = settings

    def _organization(self, org_id: str) -> Organization:
        organization = self._db.get(Organization, org_id)
        if organization is None or organization.status != Status.ACTIVE:
            raise InviteCodeError("organization_not_found", "Organization was not found.")
        return organization

    def _assert_org_access(self, org_id: str, organization: Organization) -> None:
        if org_id != organization.id:
            raise InviteCodeError("organization_mismatch", "That organization does not match the request.")

    def create(
        self,
        org_id: str,
        body: CreateInviteCodeRequest,
        *,
        user: User,
        organization: Organization,
    ) -> InviteCodeCreatedResponse:
        self._assert_org_access(org_id, organization)
        now = utcnow()
        raw_code = generate_invite_code()
        row = InviteCode(
            id=new_id(),
            org_id=organization.id,
            code_hash=hash_invite_code(raw_code, pepper=self._settings.invite_code_pepper),
            role=InviteCodeRole(body.role),
            created_by_user_id=user.id,
            expires_at=now + timedelta(days=INVITE_TTL_DAYS),
        )
        self._db.add(row)
        _audit(
            self._db,
            org_id=organization.id,
            entity_type="invite_code",
            entity_id=row.id,
            event_type="organization.invite_created",
            actor_id=user.id,
            payload={
                "invite_code_id": row.id,
                "organization_id": organization.id,
                "role": body.role,
                "created_by_user_id": user.id,
            },
        )
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise InviteCodeError("invite_not_found", "Invite code could not be created.") from exc
        self._db.refresh(row)
        return InviteCodeCreatedResponse(
            id=row.id,
            organization_id=row.org_id,
            role=_enum_value(row.role) or body.role,
            code=raw_code,
            expires_at=row.expires_at,
            created_at=row.created_at,
        )

    def list_for_organization(
        self,
        org_id: str,
        *,
        organization: Organization,
    ) -> InviteCodeListResponse:
        self._assert_org_access(org_id, organization)
        now = utcnow()
        rows = list(
            self._db.scalars(
                select(InviteCode)
                .where(InviteCode.org_id == organization.id)
                .order_by(InviteCode.created_at.desc())
            ).all()
        )
        items = [
            InviteCodeListItem(
                id=row.id,
                organization_id=row.org_id,
                role=_enum_value(row.role) or "member",
                status=_invite_status(row, now=now),
                expires_at=row.expires_at,
                used_at=row.used_at,
                used_by_user_id=row.used_by_user_id,
                created_by_user_id=row.created_by_user_id,
                created_at=row.created_at,
            )
            for row in rows
        ]
        return InviteCodeListResponse(items=items, total=len(items))

    def redeem(
        self,
        body: RedeemInviteCodeRequest,
        *,
        user: User,
    ) -> RedeemInviteCodeResponse:
        normalized = normalize_invite_code(body.code)
        if len(normalized) != 8:
            raise InviteCodeError("invite_not_found", "Invite code was not found.")
        code_hash = hash_invite_code(normalized, pepper=self._settings.invite_code_pepper)
        row = self._db.scalar(select(InviteCode).where(InviteCode.code_hash == code_hash))
        if row is None:
            raise InviteCodeError("invite_not_found", "Invite code was not found.")
        if row.used_at is not None:
            raise InviteCodeError("invite_used", "This invite code has already been used.")
        now = utcnow()
        if _aware(row.expires_at) <= now:
            raise InviteCodeError("invite_expired", "This invite code has expired.")

        organization = self._organization(row.org_id)
        existing_any = list(
            self._db.scalars(
                select(Membership).where(
                    Membership.user_id == user.id,
                    Membership.status == MembershipStatus.ACTIVE,
                )
            ).all()
        )
        for membership in existing_any:
            if membership.org_id != organization.id:
                raise InviteCodeError(
                    "organization_mismatch",
                    "You already belong to another organization.",
                )

        existing = self._db.scalar(
            select(Membership).where(
                Membership.org_id == organization.id,
                Membership.user_id == user.id,
            )
        )
        if existing is not None and existing.status == MembershipStatus.ACTIVE:
            raise InviteCodeError("organization_mismatch", "You are already a member of this organization.")

        role = Role.ADMIN if _enum_value(row.role) == InviteCodeRole.ADMIN.value else Role.MEMBER
        if existing is None:
            membership = Membership(
                id=new_id(),
                org_id=organization.id,
                user_id=user.id,
                role=role,
                status=MembershipStatus.ACTIVE,
            )
            self._db.add(membership)
        else:
            membership = existing
            membership.status = MembershipStatus.ACTIVE
            membership.role = role

        row.used_at = now
        row.used_by_user_id = user.id
        _audit(
            self._db,
            org_id=organization.id,
            entity_type="invite_code",
            entity_id=row.id,
            event_type="organization.invite_redeemed",
            actor_id=user.id,
            payload={
                "invite_code_id": row.id,
                "organization_id": organization.id,
                "membership_id": membership.id,
                "used_by_user_id": user.id,
            },
        )
        self._db.commit()
        self._db.refresh(membership)
        return RedeemInviteCodeResponse(
            organization_id=organization.id,
            organization_name=organization.name,
            membership_id=membership.id,
            role=_enum_value(row.role) or "member",
        )
