"""Authentication dependencies: AUTH_MODE=dev | firebase."""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.firebase_auth import FirebaseAuthError, verify_firebase_id_token
from app.models import (
    AuthIdentity,
    Membership,
    MembershipStatus,
    Organization,
    Role,
    Status,
    User,
    new_id,
)

bearer = HTTPBearer(auto_error=False)

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"code": "forbidden", "message": "Owner or admin membership is required."},
)

FIREBASE_PROVIDER = "firebase"


def _provision_firebase_user(db: Session, *, uid: str, email: Optional[str], name: Optional[str]) -> User:
    identity = db.scalar(
        select(AuthIdentity).where(
            AuthIdentity.provider == FIREBASE_PROVIDER,
            AuthIdentity.subject == uid,
        )
    )
    if identity is not None:
        user = db.get(User, identity.user_id)
        if user is None or user.status != Status.ACTIVE:
            raise UNAUTHORIZED
        changed = False
        if email and user.email != email:
            user.email = email
            changed = True
        if name and user.display_name != name:
            user.display_name = name
            changed = True
        if changed:
            db.commit()
            db.refresh(user)
        return user

    user = User(id=new_id(), email=email, display_name=name or (email.split("@")[0] if email else None))
    db.add(user)
    db.flush()
    db.add(AuthIdentity(id=new_id(), provider=FIREBASE_PROVIDER, subject=uid, user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    credentials_value: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> User:
    if credentials_value is None or credentials_value.scheme.lower() != "bearer":
        raise UNAUTHORIZED
    token = credentials_value.credentials
    mode = (settings.auth_mode or "dev").strip().lower()

    if mode == "dev":
        user = db.get(User, token)
        if user is None or user.status != Status.ACTIVE:
            raise UNAUTHORIZED
        return user

    if mode == "firebase":
        try:
            claims = verify_firebase_id_token(token, settings)
        except FirebaseAuthError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=exc.message,
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        return _provision_firebase_user(
            db,
            uid=claims.uid,
            email=claims.email,
            name=claims.name,
        )

    raise UNAUTHORIZED


def require_membership(
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-Id"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Membership:
    if not x_organization_id:
        raise NOT_FOUND
    membership = db.scalar(
        select(Membership)
        .join(Organization)
        .where(
            Membership.org_id == x_organization_id,
            Membership.user_id == user.id,
            Membership.status == MembershipStatus.ACTIVE,
            Organization.status == Status.ACTIVE,
        )
    )
    if membership is None:
        raise NOT_FOUND
    return membership


def require_owner_or_admin(membership: Membership = Depends(require_membership)) -> Membership:
    if membership.role not in (Role.OWNER, Role.ADMIN):
        raise FORBIDDEN
    return membership


def get_current_organization(
    membership: Membership = Depends(require_membership),
    db: Session = Depends(get_db),
) -> Organization:
    organization = db.get(Organization, membership.org_id)
    if organization is None or organization.status != Status.ACTIVE:
        raise NOT_FOUND
    return organization
