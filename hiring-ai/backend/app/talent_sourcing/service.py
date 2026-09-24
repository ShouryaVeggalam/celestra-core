"""Talent sourcing service: discover, CSV import, human import to Candidate."""

from __future__ import annotations

from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import (
    Candidate,
    CandidateDiscovery,
    CandidateStatus,
    DiscoverySource,
    DiscoveryStatus,
    HiringEvent,
    Organization,
    SourcingProject,
    User,
    new_id,
)
from app.talent_sourcing.csv_import import CsvImportError, parse_candidate_csv
from app.talent_sourcing.people_search import PeopleSearchError, search_github_people


class TalentSourcingError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


ERROR_HTTP = {
    "project_not_found": 404,
    "discovery_not_found": 404,
    "already_imported": 409,
    "no_results": 404,
    "rate_limited": 429,
    "people_search_unavailable": 502,
    "invalid_csv": 400,
    "job_not_found": 404,
}


class CreateSourcingProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    job_id: Optional[str] = None


class DiscoverRequest(BaseModel):
    project_id: str
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=20, ge=1, le=50)


class DiscoveryOut(BaseModel):
    id: str
    organization_id: str
    sourcing_project_id: str
    full_name: str
    headline: Optional[str]
    company: Optional[str]
    location: Optional[str]
    profile_url: Optional[str]
    source: str
    summary: Optional[str]
    skills: list[str]
    confidence: float
    status: str
    imported_candidate_id: Optional[str]
    created_at: str


class DiscoverResponse(BaseModel):
    project_id: str
    discoveries: list[DiscoveryOut]


class ImportDiscoveryResponse(BaseModel):
    discovery: DiscoveryOut
    candidate_id: str
    candidate_first_name: str
    candidate_last_name: str


def _discovery_out(row: CandidateDiscovery) -> DiscoveryOut:
    return DiscoveryOut(
        id=row.id,
        organization_id=row.organization_id,
        sourcing_project_id=row.sourcing_project_id,
        full_name=row.full_name,
        headline=row.headline,
        company=row.company,
        location=row.location,
        profile_url=row.profile_url,
        source=row.source.value if hasattr(row.source, "value") else str(row.source),
        summary=row.summary,
        skills=list(row.skills or []),
        confidence=row.confidence,
        status=row.status.value if hasattr(row.status, "value") else str(row.status),
        imported_candidate_id=row.imported_candidate_id,
        created_at=row.created_at.isoformat() if row.created_at else "",
    )


def _infer_source(profile_url: Optional[str]) -> DiscoverySource:
    if not profile_url:
        return DiscoverySource.MANUAL
    host = (urlparse(profile_url).hostname or "").lower()
    if "linkedin.com" in host:
        return DiscoverySource.LINKEDIN
    if "github.com" in host:
        return DiscoverySource.GITHUB
    return DiscoverySource.PORTFOLIO


def _split_name(full_name: str) -> tuple[str, str]:
    parts = [p for p in full_name.strip().split() if p]
    if not parts:
        return "Unknown", "Candidate"
    if len(parts) == 1:
        return parts[0], "Candidate"
    return parts[0], " ".join(parts[1:])


class TalentSourcingService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self._db = db
        self._settings = settings

    def _project(self, project_id: str, organization: Organization) -> SourcingProject:
        project = self._db.scalar(
            select(SourcingProject).where(
                SourcingProject.id == project_id,
                SourcingProject.organization_id == organization.id,
            )
        )
        if project is None:
            raise TalentSourcingError("project_not_found", "That sourcing project was not found.")
        return project

    def _audit(self, *, organization: Organization, entity_type: str, entity_id: str, event_type: str, actor_id: str, payload: dict) -> None:
        self._db.add(
            HiringEvent(
                org_id=organization.id,
                entity_type=entity_type,
                entity_id=entity_id,
                event_type=event_type,
                actor="user",
                actor_id=actor_id,
                payload=payload,
            )
        )

    def create_project(self, body: CreateSourcingProjectRequest, *, user: User, organization: Organization):
        project = SourcingProject(
            id=new_id(),
            organization_id=organization.id,
            name=body.name.strip(),
            job_id=body.job_id,
            created_by_user_id=user.id,
        )
        self._db.add(project)
        self._db.commit()
        self._db.refresh(project)
        return {
            "id": project.id,
            "organization_id": project.organization_id,
            "name": project.name,
            "job_id": project.job_id,
            "created_by_user_id": project.created_by_user_id,
            "created_at": project.created_at.isoformat(),
            "discoveries": [],
        }

    async def discover(self, body: DiscoverRequest, *, user: User, organization: Organization) -> DiscoverResponse:
        project = self._project(body.project_id, organization)
        try:
            profiles = await search_github_people(
                body.query,
                limit=body.limit,
                token=(self._settings.github_token or None),
            )
        except PeopleSearchError as exc:
            raise TalentSourcingError(exc.code, exc.message) from exc
        if not profiles:
            raise TalentSourcingError(
                "no_results",
                "No open-to-work profiles matched. Try different keywords, or import a recruiter CSV export.",
            )
        discoveries: list[CandidateDiscovery] = []
        for profile in profiles:
            row = CandidateDiscovery(
                id=new_id(),
                organization_id=organization.id,
                sourcing_project_id=project.id,
                full_name=profile.full_name.strip(),
                headline=profile.headline,
                company=profile.company,
                location=profile.location,
                profile_url=profile.profile_url or None,
                source=_infer_source(profile.profile_url),
                summary=profile.summary,
                skills=list(profile.skills)[:40],
                confidence=profile.confidence,
                status=DiscoveryStatus.DISCOVERED,
            )
            self._db.add(row)
            discoveries.append(row)
        self._db.flush()
        self._audit(
            organization=organization,
            entity_type="sourcing_project",
            entity_id=project.id,
            event_type="sourcing.discovered",
            actor_id=user.id,
            payload={"provider": "github", "discovery_count": len(discoveries)},
        )
        self._db.commit()
        for row in discoveries:
            self._db.refresh(row)
        return DiscoverResponse(project_id=project.id, discoveries=[_discovery_out(d) for d in discoveries])

    def import_csv_export(self, *, project_id: str, content: str, user: User, organization: Organization, limit: int = 100) -> DiscoverResponse:
        project = self._project(project_id, organization)
        try:
            rows = parse_candidate_csv(content, limit=limit)
        except CsvImportError as exc:
            raise TalentSourcingError(exc.code, exc.message) from exc
        discoveries: list[CandidateDiscovery] = []
        for row in rows:
            profile = row.profile
            discovery = CandidateDiscovery(
                id=new_id(),
                organization_id=organization.id,
                sourcing_project_id=project.id,
                full_name=profile.full_name.strip(),
                headline=profile.headline,
                company=profile.company,
                location=profile.location,
                profile_url=profile.profile_url or None,
                source=row.source,
                summary=profile.summary,
                skills=list(profile.skills)[:40],
                confidence=profile.confidence,
                status=DiscoveryStatus.DISCOVERED,
            )
            self._db.add(discovery)
            discoveries.append(discovery)
        self._db.flush()
        self._audit(
            organization=organization,
            entity_type="sourcing_project",
            entity_id=project.id,
            event_type="sourcing.csv_imported",
            actor_id=user.id,
            payload={"provider": "csv_export", "discovery_count": len(discoveries)},
        )
        self._db.commit()
        for discovery in discoveries:
            self._db.refresh(discovery)
        return DiscoverResponse(project_id=project.id, discoveries=[_discovery_out(d) for d in discoveries])

    def import_discovery(self, discovery_id: str, *, user: User, organization: Organization) -> ImportDiscoveryResponse:
        discovery = self._db.scalar(
            select(CandidateDiscovery).where(
                CandidateDiscovery.id == discovery_id,
                CandidateDiscovery.organization_id == organization.id,
            )
        )
        if discovery is None:
            raise TalentSourcingError("discovery_not_found", "That discovery was not found.")
        if discovery.status == DiscoveryStatus.IMPORTED or discovery.imported_candidate_id:
            raise TalentSourcingError("already_imported", "That discovery was already imported.")

        first, last = _split_name(discovery.full_name)
        linkedin = discovery.profile_url if discovery.source == DiscoverySource.LINKEDIN else None
        github = discovery.profile_url if discovery.source == DiscoverySource.GITHUB else None
        portfolio = discovery.profile_url if discovery.source == DiscoverySource.PORTFOLIO else None
        candidate = Candidate(
            id=new_id(),
            org_id=organization.id,
            first_name=first,
            last_name=last,
            headline=discovery.headline,
            location=discovery.location,
            linkedin_url=linkedin,
            github_url=github,
            portfolio_url=portfolio,
            summary=discovery.summary,
            skills=list(discovery.skills or []),
            status=CandidateStatus.ACTIVE,
            sourced_from_discovery_id=discovery.id,
            created_by_user_id=user.id,
        )
        self._db.add(candidate)
        self._db.flush()
        discovery.status = DiscoveryStatus.IMPORTED
        discovery.imported_candidate_id = candidate.id
        self._audit(
            organization=organization,
            entity_type="candidate_discovery",
            entity_id=discovery.id,
            event_type="sourcing.imported",
            actor_id=user.id,
            payload={"candidate_id": candidate.id, "discovery_id": discovery.id},
        )
        self._db.commit()
        self._db.refresh(discovery)
        self._db.refresh(candidate)
        return ImportDiscoveryResponse(
            discovery=_discovery_out(discovery),
            candidate_id=candidate.id,
            candidate_first_name=candidate.first_name,
            candidate_last_name=candidate.last_name,
        )
