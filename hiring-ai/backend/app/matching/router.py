"""Groq-powered match drafts. Evidence only — never a hire/reject decision."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.groq_client import GroqClient, GroqError
from app.auth import get_current_organization, get_current_user, require_membership
from app.config import Settings, get_settings
from app.database import get_db
from app.models import (
    Candidate,
    HiringEvent,
    Job,
    MatchDraft,
    Membership,
    Organization,
    User,
    new_id,
)

router = APIRouter(prefix="/api/v1/matches")

ERROR_HTTP = {
    "job_not_found": 404,
    "candidate_not_found": 404,
    "insufficient_data": 400,
    "groq_not_configured": 503,
    "groq_unauthorized": 401,
    "groq_rate_limited": 429,
    "groq_unavailable": 502,
    "malformed_output": 502,
}

SYSTEM_PROMPT = """You are a recruiting analyst for Hiring AI.
Compare one job to one candidate and return JSON only.
This is evidence for a human reviewer. Never hire, reject, rank candidates against each other, or invent contact details.
Return keys:
- score: number from 0 to 1
- summary: short paragraph
- strengths: array of short strings
- gaps: array of short strings
- evidence: array of short strings grounded in the provided facts
"""


class CreateMatchRequest(BaseModel):
    job_id: str
    candidate_id: str


class MatchOut(BaseModel):
    id: str
    org_id: str
    job_id: str
    candidate_id: str
    score: float
    summary: Optional[str]
    strengths: list[str]
    gaps: list[str]
    evidence: list[str]
    model: Optional[str]
    created_at: str


class StructureJobRequest(BaseModel):
    text: str = Field(min_length=20, max_length=20000)


class StructureJobResponse(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class StructureCandidateRequest(BaseModel):
    text: str = Field(min_length=20, max_length=20000)


class StructureCandidateResponse(BaseModel):
    first_name: str
    last_name: str
    headline: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str] = Field(default_factory=list)


def _error(exc: GroqError | Exception, *, code: str | None = None, message: str | None = None) -> JSONResponse:
    if isinstance(exc, GroqError):
        return JSONResponse(
            status_code=ERROR_HTTP.get(exc.code, 400),
            content={"detail": {"code": exc.code, "message": exc.message}},
        )
    return JSONResponse(
        status_code=ERROR_HTTP.get(code or "malformed_output", 400),
        content={"detail": {"code": code or "malformed_output", "message": message or str(exc)}},
    )


def _match_out(row: MatchDraft) -> MatchOut:
    return MatchOut(
        id=row.id,
        org_id=row.org_id,
        job_id=row.job_id,
        candidate_id=row.candidate_id,
        score=row.score,
        summary=row.summary,
        strengths=list(row.strengths or []),
        gaps=list(row.gaps or []),
        evidence=list(row.evidence or []),
        model=row.model,
        created_at=row.created_at.isoformat() if row.created_at else "",
    )


def _clamp_score(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = 0.0
    return round(min(max(score, 0.0), 1.0), 3)


def _string_list(value: Any, *, limit: int = 12) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = str(item or "").strip()
        if text:
            out.append(text[:300])
        if len(out) >= limit:
            break
    return out


@router.post("")
async def create_match(
    body: CreateMatchRequest,
    membership: Membership = Depends(require_membership),
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    del membership
    job = db.scalar(select(Job).where(Job.id == body.job_id, Job.org_id == organization.id))
    if job is None:
        return _error(Exception("missing"), code="job_not_found", message="That job was not found.")
    candidate = db.scalar(
        select(Candidate).where(Candidate.id == body.candidate_id, Candidate.org_id == organization.id)
    )
    if candidate is None:
        return _error(Exception("missing"), code="candidate_not_found", message="That candidate was not found.")
    if not (job.title or "").strip() or not (candidate.first_name or "").strip():
        return _error(
            Exception("insufficient"),
            code="insufficient_data",
            message="The job and candidate do not have enough facts to compare.",
        )

    user_prompt = {
        "job": {
            "title": job.title,
            "department": job.department,
            "location": job.location,
            "description": job.description,
        },
        "candidate": {
            "name": f"{candidate.first_name} {candidate.last_name}".strip(),
            "headline": candidate.headline,
            "location": candidate.location,
            "summary": candidate.summary,
            "skills": candidate.skills or [],
        },
    }
    client = GroqClient(settings)
    try:
        payload = await client.chat_json(
            system=SYSTEM_PROMPT,
            user=f"Compare this job and candidate. Return JSON only.\n{user_prompt}",
        )
    except GroqError as exc:
        return _error(exc)

    existing = db.scalar(
        select(MatchDraft).where(
            MatchDraft.org_id == organization.id,
            MatchDraft.job_id == job.id,
            MatchDraft.candidate_id == candidate.id,
        )
    )
    if existing is None:
        draft = MatchDraft(
            id=new_id(),
            org_id=organization.id,
            job_id=job.id,
            candidate_id=candidate.id,
            created_by_user_id=user.id,
        )
        db.add(draft)
    else:
        draft = existing

    draft.score = _clamp_score(payload.get("score"))
    draft.summary = str(payload.get("summary") or "").strip()[:4000] or None
    draft.strengths = _string_list(payload.get("strengths"))
    draft.gaps = _string_list(payload.get("gaps"))
    draft.evidence = _string_list(payload.get("evidence"))
    draft.model = settings.groq_model
    draft.created_by_user_id = user.id
    db.add(
        HiringEvent(
            org_id=organization.id,
            entity_type="match_draft",
            entity_id=draft.id,
            event_type="match.generated",
            actor="user",
            actor_id=user.id,
            payload={"job_id": job.id, "candidate_id": candidate.id, "provider": "groq", "score": draft.score},
        )
    )
    db.commit()
    db.refresh(draft)
    return _match_out(draft)


@router.get("/{match_id}")
def get_match(
    match_id: str,
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    draft = db.scalar(
        select(MatchDraft).where(MatchDraft.id == match_id, MatchDraft.org_id == organization.id)
    )
    if draft is None:
        return JSONResponse(
            status_code=404,
            content={"detail": {"code": "match_not_found", "message": "That match draft was not found."}},
        )
    return _match_out(draft)


structure_router = APIRouter(prefix="/api/v1/ai")


@structure_router.post("/structure-job", response_model=StructureJobResponse)
async def structure_job(
    body: StructureJobRequest,
    membership: Membership = Depends(require_membership),
    settings: Settings = Depends(get_settings),
):
    del membership
    client = GroqClient(settings)
    try:
        payload = await client.chat_json(
            system=(
                "Extract a job posting into JSON with keys title, department, location, description. "
                "Do not invent employer contacts. Return JSON only."
            ),
            user=body.text,
        )
    except GroqError as exc:
        return _error(exc)
    title = str(payload.get("title") or "").strip() or "Untitled role"
    return StructureJobResponse(
        title=title[:255],
        department=(str(payload.get("department") or "").strip() or None),
        location=(str(payload.get("location") or "").strip() or None),
        description=(str(payload.get("description") or body.text).strip() or None),
    )


@structure_router.post("/structure-candidate", response_model=StructureCandidateResponse)
async def structure_candidate(
    body: StructureCandidateRequest,
    membership: Membership = Depends(require_membership),
    settings: Settings = Depends(get_settings),
):
    del membership
    client = GroqClient(settings)
    try:
        payload = await client.chat_json(
            system=(
                "Extract a resume/profile into JSON with keys first_name, last_name, headline, "
                "location, summary, skills (array of strings). Never invent email or phone. Return JSON only."
            ),
            user=body.text,
        )
    except GroqError as exc:
        return _error(exc)
    first = str(payload.get("first_name") or "").strip() or "Unknown"
    last = str(payload.get("last_name") or "").strip() or "Candidate"
    skills = _string_list(payload.get("skills"), limit=40)
    return StructureCandidateResponse(
        first_name=first[:120],
        last_name=last[:120],
        headline=(str(payload.get("headline") or "").strip() or None),
        location=(str(payload.get("location") or "").strip() or None),
        summary=(str(payload.get("summary") or "").strip() or None),
        skills=skills,
    )
