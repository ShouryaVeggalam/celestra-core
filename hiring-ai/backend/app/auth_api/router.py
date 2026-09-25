"""Auth session and first-org bootstrap."""

from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import (
    HiringEvent,
    Membership,
    MembershipStatus,
    Organization,
    Role,
    Status,
    User,
    new_id,
)

router = APIRouter(prefix="/api/v1/auth")

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class MembershipOut(BaseModel):
    organization_id: str
    organization_name: str
    organization_slug: str
    membership_id: str
    role: str


class MeResponse(BaseModel):
    user_id: str
    email: Optional[str]
    display_name: Optional[str]
    memberships: list[MembershipOut]


class CreateOrganizationRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=100)


class OrganizationCreatedResponse(BaseModel):
    organization_id: str
    organization_name: str
    organization_slug: str
    membership_id: str
    role: str


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned[:100] or "org"


@router.get("/me", response_model=MeResponse)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeResponse:
    rows = list(
        db.scalars(
            select(Membership)
            .where(Membership.user_id == user.id, Membership.status == MembershipStatus.ACTIVE)
            .order_by(Membership.created_at.asc())
        ).all()
    )
    memberships: list[MembershipOut] = []
    for membership in rows:
        org = db.get(Organization, membership.org_id)
        if org is None or org.status != Status.ACTIVE:
            continue
        memberships.append(
            MembershipOut(
                organization_id=org.id,
                organization_name=org.name,
                organization_slug=org.slug,
                membership_id=membership.id,
                role=membership.role.value if hasattr(membership.role, "value") else str(membership.role),
            )
        )
    return MeResponse(
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
        memberships=memberships,
    )


@router.post("/organizations", response_model=OrganizationCreatedResponse)
def create_organization(
    body: CreateOrganizationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bootstrap the caller's first organization as owner.

    Users who already have an active membership must use invite codes instead.
    """
    existing = db.scalar(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.status == MembershipStatus.ACTIVE,
        )
    )
    if existing is not None:
        return JSONResponse(
            status_code=409,
            content={
                "detail": {
                    "code": "already_member",
                    "message": "You already belong to an organization. Use an invite code to join another.",
                }
            },
        )

    slug = body.slug.strip().lower() if body.slug.strip() else _slugify(body.name)
    if not _SLUG_RE.match(slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "invalid_slug", "message": "Slug must be lowercase letters, numbers, and hyphens."},
        )

    organization = Organization(id=new_id(), name=body.name.strip(), slug=slug, status=Status.ACTIVE)
    membership = Membership(
        id=new_id(),
        org_id=organization.id,
        user_id=user.id,
        role=Role.OWNER,
        status=MembershipStatus.ACTIVE,
    )
    db.add(organization)
    db.add(membership)
    db.add(
        HiringEvent(
            org_id=organization.id,
            entity_type="organization",
            entity_id=organization.id,
            event_type="organization.created",
            actor="user",
            actor_id=user.id,
            payload={"organization_id": organization.id, "slug": slug},
        )
    )
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "slug_taken", "message": "That organization slug is already taken."},
        ) from exc
    db.refresh(membership)
    return OrganizationCreatedResponse(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_slug=organization.slug,
        membership_id=membership.id,
        role="owner",
    )
