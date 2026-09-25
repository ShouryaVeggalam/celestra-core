"""Intelligence agents and feature-area APIs. AI drafts only — humans decide."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.groq_client import GroqClient, GroqError
from app.auth import get_current_organization, get_current_user, require_membership
from app.config import Settings, get_settings
from app.database import get_db
from app.models import (
    AgentArtifact,
    ArtifactKind,
    Candidate,
    CandidatePortalAccess,
    CandidateStatus,
    HiringDocument,
    HiringEvent,
    IntegrationLink,
    InterviewSession,
    Job,
    JobStatus,
    MatchDraft,
    Membership,
    Organization,
    Referral,
    ReviewScorecard,
    User,
    new_id,
    utcnow,
)

router = APIRouter(prefix="/api/v1")

GROQ_HTTP = {
    "groq_not_configured": 503,
    "groq_unauthorized": 401,
    "groq_rate_limited": 429,
    "groq_unavailable": 502,
    "malformed_output": 502,
}


def _groq_error(exc: GroqError) -> JSONResponse:
    return JSONResponse(
        status_code=GROQ_HTTP.get(exc.code, 400),
        content={"detail": {"code": exc.code, "message": exc.message}},
    )


def _iso(value: datetime | None) -> Optional[str]:
    return value.isoformat() if value else None


def _job(db: Session, org_id: str, job_id: Optional[str]) -> Optional[Job]:
    if not job_id:
        return None
    return db.scalar(select(Job).where(Job.id == job_id, Job.org_id == org_id))


def _candidate(db: Session, org_id: str, candidate_id: Optional[str]) -> Optional[Candidate]:
    if not candidate_id:
        return None
    return db.scalar(select(Candidate).where(Candidate.id == candidate_id, Candidate.org_id == org_id))


def _audit(
    db: Session,
    *,
    organization: Organization,
    entity_type: str,
    entity_id: str,
    event_type: str,
    actor_id: str,
    payload: dict[str, Any],
) -> None:
    db.add(
        HiringEvent(
            id=new_id(),
            org_id=organization.id,
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            actor="user",
            actor_id=actor_id,
            payload=payload,
        )
    )


def _save_artifact(
    db: Session,
    *,
    organization: Organization,
    user: User,
    kind: ArtifactKind,
    title: str,
    body: str,
    payload: dict[str, Any],
    job_id: Optional[str],
    candidate_id: Optional[str],
    model: Optional[str],
) -> AgentArtifact:
    row = AgentArtifact(
        id=new_id(),
        org_id=organization.id,
        kind=kind,
        title=title[:255],
        body=body,
        payload=payload,
        job_id=job_id,
        candidate_id=candidate_id,
        model=model,
        created_by_user_id=user.id,
    )
    db.add(row)
    _audit(
        db,
        organization=organization,
        entity_type="agent_artifact",
        entity_id=row.id,
        event_type=f"artifact.{kind.value}.created",
        actor_id=user.id,
        payload={"kind": kind.value, "title": title},
    )
    db.commit()
    db.refresh(row)
    return row


def _artifact_out(row: AgentArtifact) -> dict[str, Any]:
    return {
        "id": row.id,
        "org_id": row.org_id,
        "kind": row.kind.value if hasattr(row.kind, "value") else str(row.kind),
        "title": row.title,
        "body": row.body,
        "payload": row.payload or {},
        "job_id": row.job_id,
        "candidate_id": row.candidate_id,
        "model": row.model,
        "created_at": _iso(row.created_at),
    }


# ----- Reviews -----


class ReviewCreate(BaseModel):
    candidate_id: str
    job_id: Optional[str] = None
    overall_score: float = Field(ge=0, le=5)
    scores: dict[str, float] = Field(default_factory=dict)
    notes: Optional[str] = None
    recommendation: Optional[str] = Field(default=None, max_length=64)


@router.get("/reviews")
def list_reviews(
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    rows = db.scalars(
        select(ReviewScorecard)
        .where(ReviewScorecard.org_id == organization.id)
        .order_by(ReviewScorecard.created_at.desc())
        .limit(100)
    ).all()
    return {
        "items": [
            {
                "id": r.id,
                "candidate_id": r.candidate_id,
                "job_id": r.job_id,
                "overall_score": r.overall_score,
                "scores": r.scores or {},
                "notes": r.notes,
                "recommendation": r.recommendation,
                "created_at": _iso(r.created_at),
            }
            for r in rows
        ]
    }


@router.post("/reviews")
def create_review(
    body: ReviewCreate,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    candidate = _candidate(db, organization.id, body.candidate_id)
    if candidate is None:
        return JSONResponse(status_code=404, content={"detail": {"code": "candidate_not_found", "message": "Candidate not found."}})
    job = _job(db, organization.id, body.job_id)
    if body.job_id and job is None:
        return JSONResponse(status_code=404, content={"detail": {"code": "job_not_found", "message": "Job not found."}})
    row = ReviewScorecard(
        id=new_id(),
        org_id=organization.id,
        job_id=job.id if job else None,
        candidate_id=candidate.id,
        overall_score=body.overall_score,
        scores=body.scores,
        notes=body.notes,
        recommendation=body.recommendation,
        created_by_user_id=user.id,
    )
    db.add(row)
    _audit(
        db,
        organization=organization,
        entity_type="review_scorecard",
        entity_id=row.id,
        event_type="review.created",
        actor_id=user.id,
        payload={"candidate_id": candidate.id, "overall_score": body.overall_score},
    )
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "candidate_id": row.candidate_id,
        "job_id": row.job_id,
        "overall_score": row.overall_score,
        "scores": row.scores or {},
        "notes": row.notes,
        "recommendation": row.recommendation,
        "created_at": _iso(row.created_at),
    }


# ----- Interviews -----


class InterviewCreate(BaseModel):
    candidate_id: str
    job_id: Optional[str] = None
    title: str = Field(min_length=2, max_length=255)
    notes: Optional[str] = None
    generate_with_ai: bool = True


@router.get("/interviews")
def list_interviews(
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    rows = db.scalars(
        select(InterviewSession)
        .where(InterviewSession.org_id == organization.id)
        .order_by(InterviewSession.created_at.desc())
        .limit(100)
    ).all()
    return {
        "items": [
            {
                "id": r.id,
                "candidate_id": r.candidate_id,
                "job_id": r.job_id,
                "title": r.title,
                "questions": r.questions or [],
                "notes": r.notes,
                "summary": r.summary,
                "model": r.model,
                "created_at": _iso(r.created_at),
            }
            for r in rows
        ]
    }


@router.post("/interviews")
async def create_interview(
    body: InterviewCreate,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    del membership
    candidate = _candidate(db, organization.id, body.candidate_id)
    if candidate is None:
        return JSONResponse(status_code=404, content={"detail": {"code": "candidate_not_found", "message": "Candidate not found."}})
    job = _job(db, organization.id, body.job_id)
    questions: list[str] = [
        "Walk me through a recent project similar to this role.",
        "How do you handle ambiguity and shifting priorities?",
        "What would success look like in your first 90 days?",
    ]
    summary = None
    model = None
    if body.generate_with_ai:
        client = GroqClient(settings)
        try:
            payload = await client.chat_json(
                system=(
                    "You are an interview copilot. Return JSON with keys questions (array of strings) "
                    "and summary (short interviewer brief). Never schedule meetings or invent contacts."
                ),
                user=(
                    f"Job: {job.title if job else 'General role'}\n"
                    f"Job description: {(job.description if job else '') or 'n/a'}\n"
                    f"Candidate: {candidate.first_name} {candidate.last_name}\n"
                    f"Headline: {candidate.headline or ''}\n"
                    f"Summary: {candidate.summary or ''}\n"
                    f"Skills: {', '.join(candidate.skills or [])}"
                ),
            )
            qs = payload.get("questions")
            if isinstance(qs, list) and qs:
                questions = [str(q).strip() for q in qs if str(q).strip()][:12]
            summary = str(payload.get("summary") or "").strip() or None
            model = settings.groq_model
        except GroqError as exc:
            return _groq_error(exc)
    row = InterviewSession(
        id=new_id(),
        org_id=organization.id,
        job_id=job.id if job else None,
        candidate_id=candidate.id,
        title=body.title.strip(),
        questions=questions,
        notes=body.notes,
        summary=summary,
        model=model,
        created_by_user_id=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "candidate_id": row.candidate_id,
        "job_id": row.job_id,
        "title": row.title,
        "questions": row.questions or [],
        "notes": row.notes,
        "summary": row.summary,
        "model": row.model,
        "created_at": _iso(row.created_at),
    }


# ----- Agent draft generators -----


class AgentDraftRequest(BaseModel):
    job_id: Optional[str] = None
    candidate_id: Optional[str] = None
    topic: Optional[str] = Field(default=None, max_length=500)
    extra_context: Optional[str] = Field(default=None, max_length=8000)


@router.get("/agents/artifacts")
def list_artifacts(
    kind: Optional[str] = None,
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    stmt = select(AgentArtifact).where(AgentArtifact.org_id == organization.id)
    if kind:
        stmt = stmt.where(AgentArtifact.kind == kind)
    rows = db.scalars(stmt.order_by(AgentArtifact.created_at.desc()).limit(100)).all()
    return {"items": [_artifact_out(r) for r in rows]}


@router.post("/agents/outreach")
async def draft_outreach(
    body: AgentDraftRequest,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    del membership
    candidate = _candidate(db, organization.id, body.candidate_id)
    if candidate is None:
        return JSONResponse(status_code=404, content={"detail": {"code": "candidate_not_found", "message": "Candidate not found."}})
    job = _job(db, organization.id, body.job_id)
    client = GroqClient(settings)
    try:
        payload = await client.chat_json(
            system=(
                "Write recruiter outreach draft JSON with keys subject, body, tone. "
                "Do not send email. Do not invent phone numbers. Keep it concise and human."
            ),
            user=(
                f"Org: {organization.name}\nRole: {job.title if job else 'open role'}\n"
                f"Candidate: {candidate.first_name} {candidate.last_name}\n"
                f"Headline: {candidate.headline or ''}\nContext: {body.extra_context or ''}"
            ),
        )
    except GroqError as exc:
        return _groq_error(exc)
    subject = str(payload.get("subject") or f"Opportunity: {job.title if job else 'role'}").strip()
    text = str(payload.get("body") or "").strip()
    row = _save_artifact(
        db,
        organization=organization,
        user=user,
        kind=ArtifactKind.OUTREACH,
        title=subject[:255],
        body=text,
        payload=payload,
        job_id=job.id if job else None,
        candidate_id=candidate.id,
        model=settings.groq_model,
    )
    return _artifact_out(row)


@router.post("/agents/skills")
async def skills_intelligence(
    body: AgentDraftRequest,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    del membership
    candidate = _candidate(db, organization.id, body.candidate_id)
    if candidate is None:
        return JSONResponse(status_code=404, content={"detail": {"code": "candidate_not_found", "message": "Candidate not found."}})
    client = GroqClient(settings)
    try:
        payload = await client.chat_json(
            system=(
                "Build a skills intelligence JSON with keys core_skills (array), adjacent_skills (array), "
                "evidence (array), gaps (array). Ground only in provided profile text."
            ),
            user=(
                f"Name: {candidate.first_name} {candidate.last_name}\n"
                f"Headline: {candidate.headline or ''}\nSummary: {candidate.summary or ''}\n"
                f"Listed skills: {', '.join(candidate.skills or [])}"
            ),
        )
    except GroqError as exc:
        return _groq_error(exc)
    row = _save_artifact(
        db,
        organization=organization,
        user=user,
        kind=ArtifactKind.SKILLS,
        title=f"Skills graph — {candidate.first_name} {candidate.last_name}",
        body=str(payload.get("evidence") or ""),
        payload=payload,
        job_id=None,
        candidate_id=candidate.id,
        model=settings.groq_model,
    )
    return _artifact_out(row)


@router.post("/agents/compensation")
async def compensation_intelligence(
    body: AgentDraftRequest,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    del membership
    job = _job(db, organization.id, body.job_id)
    if job is None:
        return JSONResponse(status_code=404, content={"detail": {"code": "job_not_found", "message": "Job not found."}})
    client = GroqClient(settings)
    try:
        payload = await client.chat_json(
            system=(
                "Provide compensation guidance JSON with keys currency, low, mid, high, rationale, caveats. "
                "This is advisory only, not an offer. Mark uncertainty clearly."
            ),
            user=(
                f"Role: {job.title}\nLocation: {job.location or 'unspecified'}\n"
                f"Department: {job.department or ''}\nDescription: {job.description or ''}\n"
                f"Extra: {body.extra_context or ''}"
            ),
        )
    except GroqError as exc:
        return _groq_error(exc)
    row = _save_artifact(
        db,
        organization=organization,
        user=user,
        kind=ArtifactKind.COMPENSATION,
        title=f"Compensation guidance — {job.title}",
        body=str(payload.get("rationale") or ""),
        payload=payload,
        job_id=job.id,
        candidate_id=None,
        model=settings.groq_model,
    )
    return _artifact_out(row)


@router.post("/agents/forecast")
async def hiring_forecast(
    body: AgentDraftRequest,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    del membership
    open_jobs = db.scalar(
        select(func.count()).select_from(Job).where(Job.org_id == organization.id, Job.status == JobStatus.OPEN)
    ) or 0
    active = db.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(Candidate.org_id == organization.id, Candidate.status == CandidateStatus.ACTIVE)
    ) or 0
    hired = db.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(Candidate.org_id == organization.id, Candidate.status == CandidateStatus.HIRED)
    ) or 0
    metrics = {
        "open_jobs": int(open_jobs),
        "active_candidates": int(active),
        "hired_candidates": int(hired),
        "pipeline_per_open_role": round(int(active) / int(open_jobs), 2) if open_jobs else None,
    }
    client = GroqClient(settings)
    narrative = ""
    model = None
    try:
        payload = await client.chat_json(
            system=(
                "You are a hiring forecast analyst. Return JSON with keys outlook, risks (array), "
                "recommended_actions (array). Use only provided metrics. No autonomous actions."
            ),
            user=f"Org: {organization.name}\nMetrics: {metrics}\nTopic: {body.topic or 'quarterly hiring'}",
        )
        narrative = str(payload.get("outlook") or "")
        metrics["ai"] = payload
        model = settings.groq_model
    except GroqError as exc:
        return _groq_error(exc)
    row = _save_artifact(
        db,
        organization=organization,
        user=user,
        kind=ArtifactKind.FORECAST,
        title=f"Hiring forecast — {organization.name}",
        body=narrative,
        payload=metrics,
        job_id=None,
        candidate_id=None,
        model=model,
    )
    return _artifact_out(row)


@router.post("/agents/playbooks")
async def create_playbook(
    body: AgentDraftRequest,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    del membership
    topic = (body.topic or "Standard hiring playbook").strip()
    client = GroqClient(settings)
    try:
        payload = await client.chat_json(
            system=(
                "Create a reusable hiring playbook JSON with keys title, stages (array of {name, checklist}), "
                "guardrails (array). Emphasize human approval for hire/reject/email/schedule."
            ),
            user=f"Organization: {organization.name}\nTopic: {topic}\nContext: {body.extra_context or ''}",
        )
    except GroqError as exc:
        return _groq_error(exc)
    title = str(payload.get("title") or topic)[:255]
    row = _save_artifact(
        db,
        organization=organization,
        user=user,
        kind=ArtifactKind.PLAYBOOK,
        title=title,
        body="",
        payload=payload,
        job_id=None,
        candidate_id=None,
        model=settings.groq_model,
    )
    return _artifact_out(row)


@router.post("/agents/hiring-chief")
async def hiring_chief(
    body: AgentDraftRequest,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    del membership
    stats = {
        "open_jobs": db.scalar(select(func.count()).select_from(Job).where(Job.org_id == organization.id, Job.status == JobStatus.OPEN)) or 0,
        "active_candidates": db.scalar(select(func.count()).select_from(Candidate).where(Candidate.org_id == organization.id, Candidate.status == CandidateStatus.ACTIVE)) or 0,
        "hired": db.scalar(select(func.count()).select_from(Candidate).where(Candidate.org_id == organization.id, Candidate.status == CandidateStatus.HIRED)) or 0,
        "matches": db.scalar(select(func.count()).select_from(MatchDraft).where(MatchDraft.org_id == organization.id)) or 0,
        "reviews": db.scalar(select(func.count()).select_from(ReviewScorecard).where(ReviewScorecard.org_id == organization.id)) or 0,
    }
    client = GroqClient(settings)
    try:
        payload = await client.chat_json(
            system=(
                "You are Hiring Chief. Return JSON with keys priorities (array), risks (array), "
                "executive_summary. Advise humans; never hire or reject."
            ),
            user=f"Org: {organization.name}\nStats: {stats}\nFocus: {body.topic or 'this week'}",
        )
    except GroqError as exc:
        return _groq_error(exc)
    row = _save_artifact(
        db,
        organization=organization,
        user=user,
        kind=ArtifactKind.HIRING_CHIEF,
        title=f"Hiring Chief brief — {organization.name}",
        body=str(payload.get("executive_summary") or ""),
        payload={"stats": stats, "ai": payload},
        job_id=None,
        candidate_id=None,
        model=settings.groq_model,
    )
    return _artifact_out(row)


@router.post("/agents/autonomous-prep")
async def autonomous_prep(
    body: AgentDraftRequest,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    del membership
    client = GroqClient(settings)
    try:
        payload = await client.chat_json(
            system=(
                "Propose SAFE preparation tasks only as JSON with keys tasks (array of {title, rationale, requires_human}). "
                "Forbidden: sending email, scheduling, hiring, rejecting, or contacting candidates."
            ),
            user=f"Org: {organization.name}\nRequest: {body.topic or 'prep next hiring actions'}\nContext: {body.extra_context or ''}",
        )
    except GroqError as exc:
        return _groq_error(exc)
    tasks = payload.get("tasks") if isinstance(payload.get("tasks"), list) else []
    for task in tasks:
        if isinstance(task, dict):
            task["requires_human"] = True
            task["auto_execute"] = False
    row = _save_artifact(
        db,
        organization=organization,
        user=user,
        kind=ArtifactKind.AUTONOMOUS_PREP,
        title="Autonomous prep pack (human approval required)",
        body="These are preparation suggestions only. Nothing was executed.",
        payload={"tasks": tasks},
        job_id=body.job_id,
        candidate_id=body.candidate_id,
        model=settings.groq_model,
    )
    return _artifact_out(row)


# ----- Referrals -----


class ReferralCreate(BaseModel):
    referrer_name: str = Field(min_length=1, max_length=255)
    referrer_email: Optional[str] = None
    candidate_name: str = Field(min_length=1, max_length=255)
    candidate_email: Optional[str] = None
    job_id: Optional[str] = None
    notes: Optional[str] = None
    enrich_with_ai: bool = True


@router.get("/referrals")
def list_referrals(
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    rows = db.scalars(select(Referral).where(Referral.org_id == organization.id).order_by(Referral.created_at.desc()).limit(100)).all()
    return {
        "items": [
            {
                "id": r.id,
                "referrer_name": r.referrer_name,
                "referrer_email": r.referrer_email,
                "candidate_name": r.candidate_name,
                "candidate_email": r.candidate_email,
                "job_id": r.job_id,
                "notes": r.notes,
                "status": r.status,
                "intelligence": r.intelligence,
                "created_at": _iso(r.created_at),
            }
            for r in rows
        ]
    }


@router.post("/referrals")
async def create_referral(
    body: ReferralCreate,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    del membership
    job = _job(db, organization.id, body.job_id)
    intelligence = None
    if body.enrich_with_ai:
        client = GroqClient(settings)
        try:
            intelligence = await client.chat_json(
                system=(
                    "Referral intelligence JSON with keys fit_notes, screening_questions (array), risk_flags (array). "
                    "Do not invent contact details beyond provided fields."
                ),
                user=(
                    f"Referrer: {body.referrer_name}\nCandidate: {body.candidate_name}\n"
                    f"Role: {job.title if job else 'unspecified'}\nNotes: {body.notes or ''}"
                ),
            )
        except GroqError as exc:
            return _groq_error(exc)
    row = Referral(
        id=new_id(),
        org_id=organization.id,
        job_id=job.id if job else None,
        referrer_name=body.referrer_name.strip(),
        referrer_email=body.referrer_email,
        candidate_name=body.candidate_name.strip(),
        candidate_email=body.candidate_email,
        notes=body.notes,
        status="new",
        intelligence=intelligence,
        created_by_user_id=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "referrer_name": row.referrer_name,
        "candidate_name": row.candidate_name,
        "status": row.status,
        "intelligence": row.intelligence,
        "created_at": _iso(row.created_at),
    }


# ----- Documents -----


class DocumentCreate(BaseModel):
    doc_type: str = Field(pattern="^(hiring_brief|offer_letter)$")
    job_id: Optional[str] = None
    candidate_id: Optional[str] = None
    extra_context: Optional[str] = None


@router.get("/documents")
def list_documents(
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    rows = db.scalars(
        select(HiringDocument).where(HiringDocument.org_id == organization.id).order_by(HiringDocument.created_at.desc()).limit(100)
    ).all()
    return {
        "items": [
            {
                "id": r.id,
                "doc_type": r.doc_type,
                "title": r.title,
                "body": r.body,
                "job_id": r.job_id,
                "candidate_id": r.candidate_id,
                "model": r.model,
                "created_at": _iso(r.created_at),
            }
            for r in rows
        ]
    }


@router.post("/documents")
async def create_document(
    body: DocumentCreate,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    del membership
    job = _job(db, organization.id, body.job_id)
    candidate = _candidate(db, organization.id, body.candidate_id)
    client = GroqClient(settings)
    if body.doc_type == "hiring_brief":
        system = "Write a hiring brief as JSON with keys title, body_markdown. Evidence for humans only."
        prompt = f"Org: {organization.name}\nJob: {job.title if job else 'role'}\nDesc: {job.description if job else ''}\n{body.extra_context or ''}"
    else:
        system = (
            "Draft an offer letter as JSON with keys title, body_markdown. "
            "Do not finalize compensation. Mark placeholders like [SALARY] for humans."
        )
        prompt = (
            f"Org: {organization.name}\nJob: {job.title if job else 'role'}\n"
            f"Candidate: {candidate.first_name + ' ' + candidate.last_name if candidate else 'Candidate'}\n"
            f"{body.extra_context or ''}"
        )
    try:
        payload = await client.chat_json(system=system, user=prompt)
    except GroqError as exc:
        return _groq_error(exc)
    title = str(payload.get("title") or body.doc_type.replace("_", " ").title())[:255]
    body_md = str(payload.get("body_markdown") or payload.get("body") or "").strip()
    if not body_md:
        return JSONResponse(status_code=502, content={"detail": {"code": "malformed_output", "message": "Empty document draft."}})
    row = HiringDocument(
        id=new_id(),
        org_id=organization.id,
        doc_type=body.doc_type,
        title=title,
        body=body_md,
        job_id=job.id if job else None,
        candidate_id=candidate.id if candidate else None,
        model=settings.groq_model,
        created_by_user_id=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "doc_type": row.doc_type,
        "title": row.title,
        "body": row.body,
        "job_id": row.job_id,
        "candidate_id": row.candidate_id,
        "model": row.model,
        "created_at": _iso(row.created_at),
    }


@router.get("/documents/{document_id}/export.txt")
def export_document_text(
    document_id: str,
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    row = db.scalar(
        select(HiringDocument).where(HiringDocument.id == document_id, HiringDocument.org_id == organization.id)
    )
    if row is None:
        return JSONResponse(status_code=404, content={"detail": {"code": "document_not_found", "message": "Document not found."}})
    return PlainTextResponse(f"{row.title}\n\n{row.body}", media_type="text/plain")


# ----- Candidate portal -----


class PortalCreate(BaseModel):
    candidate_id: str
    offer_title: Optional[str] = None
    offer_body: Optional[str] = None


class PortalRespond(BaseModel):
    response_status: str = Field(pattern="^(accepted|declined|maybe)$")
    response_note: Optional[str] = None


@router.post("/candidate-portal")
def create_portal_access(
    body: PortalCreate,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    candidate = _candidate(db, organization.id, body.candidate_id)
    if candidate is None:
        return JSONResponse(status_code=404, content={"detail": {"code": "candidate_not_found", "message": "Candidate not found."}})
    token = secrets.token_urlsafe(24)
    row = CandidatePortalAccess(
        id=new_id(),
        org_id=organization.id,
        candidate_id=candidate.id,
        token=token,
        offer_title=body.offer_title or f"Offer for {candidate.first_name}",
        offer_body=body.offer_body or "Please review this draft offer with your recruiter. This is not legally binding until countersigned.",
        response_status="pending",
        created_by_user_id=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "token": row.token,
        "candidate_id": row.candidate_id,
        "offer_title": row.offer_title,
        "offer_body": row.offer_body,
        "response_status": row.response_status,
        "portal_path": f"/portal/{row.token}",
        "created_at": _iso(row.created_at),
    }


@router.get("/candidate-portal")
def list_portal_access(
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    rows = db.scalars(
        select(CandidatePortalAccess)
        .where(CandidatePortalAccess.org_id == organization.id)
        .order_by(CandidatePortalAccess.created_at.desc())
        .limit(100)
    ).all()
    return {
        "items": [
            {
                "id": r.id,
                "token": r.token,
                "candidate_id": r.candidate_id,
                "offer_title": r.offer_title,
                "response_status": r.response_status,
                "response_note": r.response_note,
                "portal_path": f"/portal/{r.token}",
                "created_at": _iso(r.created_at),
                "responded_at": _iso(r.responded_at),
            }
            for r in rows
        ]
    }


# Public portal handlers live on main app; keep respond here under same router with public flag via separate mount.


public_router = APIRouter(prefix="/api/v1")


@public_router.get("/candidate-portal/{token}")
def public_portal_get(token: str, db: Session = Depends(get_db)):
    row = db.scalar(select(CandidatePortalAccess).where(CandidatePortalAccess.token == token))
    if row is None:
        return JSONResponse(status_code=404, content={"detail": {"code": "portal_not_found", "message": "Portal link not found."}})
    candidate = db.get(Candidate, row.candidate_id)
    return {
        "token": row.token,
        "status": row.response_status,
        "offer_title": row.offer_title,
        "offer_body": row.offer_body,
        "candidate_name": f"{candidate.first_name} {candidate.last_name}" if candidate else None,
        "response_note": row.response_note,
    }


@public_router.post("/candidate-portal/{token}/respond")
def public_portal_respond(token: str, body: PortalRespond, db: Session = Depends(get_db)):
    row = db.scalar(select(CandidatePortalAccess).where(CandidatePortalAccess.token == token))
    if row is None:
        return JSONResponse(status_code=404, content={"detail": {"code": "portal_not_found", "message": "Portal link not found."}})
    row.response_status = body.response_status
    row.response_note = body.response_note
    row.responded_at = utcnow()
    db.commit()
    db.refresh(row)
    return {"token": row.token, "response_status": row.response_status, "responded_at": _iso(row.responded_at)}


# ----- Analytics + Integrations -----


@router.get("/analytics/summary")
def analytics_summary(
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    by_status = {
        status.value: db.scalar(
            select(func.count()).select_from(Candidate).where(Candidate.org_id == organization.id, Candidate.status == status)
        )
        or 0
        for status in CandidateStatus
    }
    return {
        "organization_id": organization.id,
        "open_jobs": db.scalar(select(func.count()).select_from(Job).where(Job.org_id == organization.id, Job.status == JobStatus.OPEN)) or 0,
        "candidates_by_status": by_status,
        "match_drafts": db.scalar(select(func.count()).select_from(MatchDraft).where(MatchDraft.org_id == organization.id)) or 0,
        "reviews": db.scalar(select(func.count()).select_from(ReviewScorecard).where(ReviewScorecard.org_id == organization.id)) or 0,
        "interviews": db.scalar(select(func.count()).select_from(InterviewSession).where(InterviewSession.org_id == organization.id)) or 0,
        "referrals": db.scalar(select(func.count()).select_from(Referral).where(Referral.org_id == organization.id)) or 0,
        "documents": db.scalar(select(func.count()).select_from(HiringDocument).where(HiringDocument.org_id == organization.id)) or 0,
        "portal_links": db.scalar(select(func.count()).select_from(CandidatePortalAccess).where(CandidatePortalAccess.org_id == organization.id)) or 0,
    }


class IntegrationCreate(BaseModel):
    provider: str = Field(min_length=2, max_length=64)
    notes: Optional[str] = None


@router.get("/integrations")
def list_integrations(
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    del membership
    rows = db.scalars(
        select(IntegrationLink).where(IntegrationLink.org_id == organization.id).order_by(IntegrationLink.created_at.desc())
    ).all()
    builtins = [
        {"provider": "firebase_auth", "status": "connected" if (settings.auth_mode or "").lower() == "firebase" else "available"},
        {"provider": "groq", "status": "connected" if (settings.groq_api_key or "").strip() else "needs_key"},
        {"provider": "github_sourcing", "status": "connected"},
        {"provider": "neon_postgres", "status": "connected"},
    ]
    return {
        "builtins": builtins,
        "items": [
            {
                "id": r.id,
                "provider": r.provider,
                "status": r.status,
                "notes": r.notes,
                "created_at": _iso(r.created_at),
            }
            for r in rows
        ],
    }


@router.post("/integrations")
def create_integration(
    body: IntegrationCreate,
    user: User = Depends(get_current_user),
    membership: Membership = Depends(require_membership),
    organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    del membership
    row = IntegrationLink(
        id=new_id(),
        org_id=organization.id,
        provider=body.provider.strip().lower(),
        status="configured",
        notes=body.notes,
        created_by_user_id=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "provider": row.provider,
        "status": row.status,
        "notes": row.notes,
        "created_at": _iso(row.created_at),
    }
