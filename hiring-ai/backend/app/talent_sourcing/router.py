from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth import get_current_organization, get_current_user, require_membership
from app.config import Settings, get_settings
from app.database import get_db
from app.models import Membership, Organization, User
from app.talent_sourcing.service import (
    CreateSourcingProjectRequest,
    DiscoverRequest,
    ERROR_HTTP,
    TalentSourcingError,
    TalentSourcingService,
)

router = APIRouter(prefix="/api/v1/source")


def get_service(db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> TalentSourcingService:
    return TalentSourcingService(db, settings)


def _error(exc: TalentSourcingError) -> JSONResponse:
    return JSONResponse(
        status_code=ERROR_HTTP.get(exc.code, 400),
        content={"detail": {"code": exc.code, "message": exc.message}},
    )


@router.post("/projects")
def create_project(
    body: CreateSourcingProjectRequest,
    membership: Membership = Depends(require_membership),
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    service: TalentSourcingService = Depends(get_service),
):
    del membership
    return service.create_project(body, user=user, organization=organization)


@router.post("/discover")
async def discover(
    body: DiscoverRequest,
    membership: Membership = Depends(require_membership),
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    service: TalentSourcingService = Depends(get_service),
):
    del membership
    try:
        return await service.discover(body, user=user, organization=organization)
    except TalentSourcingError as exc:
        return _error(exc)


@router.post("/projects/{project_id}/import-csv")
async def import_csv(
    project_id: str,
    membership: Membership = Depends(require_membership),
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    service: TalentSourcingService = Depends(get_service),
    file: UploadFile = File(...),
):
    del membership
    raw = await file.read()
    if len(raw) > 1_000_000:
        return JSONResponse(
            status_code=400,
            content={"detail": {"code": "invalid_csv", "message": "CSV file is too large (max 1MB)."}},
        )
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return JSONResponse(
            status_code=400,
            content={"detail": {"code": "invalid_csv", "message": "CSV must be UTF-8 text."}},
        )
    try:
        return service.import_csv_export(
            project_id=project_id,
            content=content,
            user=user,
            organization=organization,
        )
    except TalentSourcingError as exc:
        return _error(exc)


@router.post("/import/{discovery_id}")
def import_discovery(
    discovery_id: str,
    membership: Membership = Depends(require_membership),
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    service: TalentSourcingService = Depends(get_service),
):
    del membership
    try:
        return service.import_discovery(discovery_id, user=user, organization=organization)
    except TalentSourcingError as exc:
        return _error(exc)
