from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import get_current_organization, get_current_user, require_membership
from app.database import get_db
from app.models import Candidate, CandidateStatus, Membership, Organization, User, new_id

router = APIRouter(prefix="/api/v1/candidates")


class CreateCandidateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    email: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str] = Field(default_factory=list)


class UpdateCandidateStatusRequest(BaseModel):
    status: str


class CandidateOut(BaseModel):
    id: str
    org_id: str
    first_name: str
    last_name: str
    email: Optional[str]
    headline: Optional[str]
    location: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_url: Optional[str]
    summary: Optional[str]
    skills: list[str]
    status: str
    sourced_from_discovery_id: Optional[str]
    created_at: str


class CandidateListResponse(BaseModel):
    items: list[CandidateOut]
    total: int
    limit: int
    offset: int


def _out(row: Candidate) -> CandidateOut:
    return CandidateOut(
        id=row.id,
        org_id=row.org_id,
        first_name=row.first_name,
        last_name=row.last_name,
        email=row.email,
        headline=row.headline,
        location=row.location,
        linkedin_url=row.linkedin_url,
        github_url=row.github_url,
        portfolio_url=row.portfolio_url,
        summary=row.summary,
        skills=list(row.skills or []),
        status=row.status.value if hasattr(row.status, "value") else str(row.status),
        sourced_from_discovery_id=row.sourced_from_discovery_id,
        created_at=row.created_at.isoformat() if row.created_at else "",
    )


@router.get("")
def list_candidates(
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    del membership
    total = db.scalar(select(func.count()).select_from(Candidate).where(Candidate.org_id == organization.id)) or 0
    rows = list(
        db.scalars(
            select(Candidate)
            .where(Candidate.org_id == organization.id)
            .order_by(Candidate.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()
    )
    return CandidateListResponse(items=[_out(r) for r in rows], total=total, limit=limit, offset=offset)


@router.post("")
def create_candidate(
    body: CreateCandidateRequest,
    membership: Membership = Depends(require_membership),
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    candidate = Candidate(
        id=new_id(),
        org_id=organization.id,
        first_name=body.first_name.strip(),
        last_name=body.last_name.strip(),
        email=body.email,
        headline=body.headline,
        location=body.location,
        summary=body.summary,
        skills=list(body.skills)[:40],
        status=CandidateStatus.ACTIVE,
        created_by_user_id=user.id,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return _out(candidate)


@router.post("/{candidate_id}/status")
def update_status(
    candidate_id: str,
    body: UpdateCandidateStatusRequest,
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    try:
        status = CandidateStatus(body.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "invalid_status", "message": "Invalid candidate status."}) from exc
    candidate = db.scalar(
        select(Candidate).where(Candidate.id == candidate_id, Candidate.org_id == organization.id)
    )
    if candidate is None:
        raise HTTPException(status_code=404, detail={"code": "candidate_not_found", "message": "Candidate not found."})
    candidate.status = status
    db.commit()
    db.refresh(candidate)
    return _out(candidate)
