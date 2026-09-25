from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import get_current_organization, get_current_user, require_membership
from app.database import get_db
from app.models import Job, JobStatus, Membership, Organization, User, new_id

router = APIRouter(prefix="/api/v1/jobs")


class CreateJobRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    department: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class JobOut(BaseModel):
    id: str
    org_id: str
    title: str
    department: Optional[str]
    location: Optional[str]
    description: Optional[str]
    status: str
    created_at: str


class JobListResponse(BaseModel):
    items: list[JobOut]
    total: int
    limit: int
    offset: int


def _out(job: Job) -> JobOut:
    return JobOut(
        id=job.id,
        org_id=job.org_id,
        title=job.title,
        department=job.department,
        location=job.location,
        description=job.description,
        status=job.status.value if hasattr(job.status, "value") else str(job.status),
        created_at=job.created_at.isoformat() if job.created_at else "",
    )


@router.get("")
def list_jobs(
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    del membership
    total = db.scalar(select(func.count()).select_from(Job).where(Job.org_id == organization.id)) or 0
    rows = list(
        db.scalars(
            select(Job)
            .where(Job.org_id == organization.id)
            .order_by(Job.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()
    )
    return JobListResponse(items=[_out(r) for r in rows], total=total, limit=limit, offset=offset)


@router.post("")
def create_job(
    body: CreateJobRequest,
    membership: Membership = Depends(require_membership),
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    job = Job(
        id=new_id(),
        org_id=organization.id,
        title=body.title.strip(),
        department=(body.department or None),
        location=(body.location or None),
        description=(body.description or None),
        status=JobStatus.OPEN,
        created_by_user_id=user.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _out(job)
