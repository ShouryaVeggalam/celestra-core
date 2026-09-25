from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth import get_current_organization, get_current_user, require_owner_or_admin
from app.config import Settings, get_settings
from app.database import get_db
from app.invite_codes.errors import InviteCodeError
from app.invite_codes.schemas import CreateInviteCodeRequest, RedeemInviteCodeRequest
from app.invite_codes.service import ERROR_HTTP, InviteCodeService
from app.models import Membership, Organization, User

router = APIRouter(prefix="/api/v1")


def get_invite_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> InviteCodeService:
    return InviteCodeService(db, settings)


def _error(exc: InviteCodeError) -> JSONResponse:
    return JSONResponse(
        status_code=ERROR_HTTP.get(exc.code, 400),
        content={"detail": {"code": exc.code, "message": exc.message}},
    )


@router.post("/organizations/{org_id}/invite-codes")
def create_invite(
    org_id: str,
    body: CreateInviteCodeRequest,
    membership: Membership = Depends(require_owner_or_admin),
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    service: InviteCodeService = Depends(get_invite_service),
):
    del membership
    try:
        return service.create(org_id, body, user=user, organization=organization)
    except InviteCodeError as exc:
        return _error(exc)


@router.get("/organizations/{org_id}/invite-codes")
def list_invites(
    org_id: str,
    membership: Membership = Depends(require_owner_or_admin),
    organization: Organization = Depends(get_current_organization),
    service: InviteCodeService = Depends(get_invite_service),
):
    del membership
    try:
        return service.list_for_organization(org_id, organization=organization)
    except InviteCodeError as exc:
        return _error(exc)


@router.post("/invite-codes/redeem")
def redeem_invite(
    body: RedeemInviteCodeRequest,
    user: User = Depends(get_current_user),
    service: InviteCodeService = Depends(get_invite_service),
):
    try:
        return service.redeem(body, user=user)
    except InviteCodeError as exc:
        return _error(exc)
