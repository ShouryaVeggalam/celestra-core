"""CSV import of recruiter-owned candidate exports. Never scrapes job boards."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from app.models import DiscoverySource
from app.talent_sourcing.people_search import PeopleProfile, _clean_text

BOARD_SOURCES = frozenset({"naukri", "internshala", "apna", "wellfound", "linkedin", "manual", "github"})


@dataclass(frozen=True)
class CsvImportRow:
    profile: PeopleProfile
    source: DiscoverySource
    board_label: Optional[str]


class CsvImportError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def _norm_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _infer_source(profile_url: Optional[str], source_hint: Optional[str]) -> tuple[DiscoverySource, Optional[str]]:
    hint = (source_hint or "").strip().lower()
    board = hint if hint in BOARD_SOURCES else None
    if profile_url:
        host = (urlparse(profile_url).hostname or "").lower()
        if "linkedin.com" in host:
            return DiscoverySource.LINKEDIN, board or "linkedin"
        if "github.com" in host:
            return DiscoverySource.GITHUB, board or "github"
        if host:
            return DiscoverySource.PORTFOLIO, board or "manual"
    if hint == "linkedin":
        return DiscoverySource.LINKEDIN, "linkedin"
    if hint == "github":
        return DiscoverySource.GITHUB, "github"
    return DiscoverySource.MANUAL, board or hint or "manual"


def _truthy(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "open", "looking"}


def parse_candidate_csv(content: str, *, limit: int = 100) -> list[CsvImportRow]:
    if not content or not content.strip():
        raise CsvImportError("invalid_csv", "CSV file is empty.")
    text = content.lstrip("\ufeff")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise CsvImportError("invalid_csv", "CSV must include a header row with full_name.")
    normalized = {_norm_header(name) for name in reader.fieldnames if name}
    if "full_name" not in normalized and "name" not in normalized:
        raise CsvImportError(
            "invalid_csv",
            "CSV must include a full_name (or name) column. Email/phone columns are ignored.",
        )
    rows: list[CsvImportRow] = []
    for raw in reader:
        if len(rows) >= limit:
            break
        mapped = {_norm_header(k): (v or "").strip() for k, v in raw.items() if k}
        full_name = _clean_text(mapped.get("full_name") or mapped.get("name"), max_len=255) or ""
        if not full_name:
            continue
        headline = _clean_text(mapped.get("headline") or mapped.get("title"), max_len=500)
        company = _clean_text(mapped.get("company") or mapped.get("organization"), max_len=255)
        location = _clean_text(mapped.get("location") or mapped.get("city"), max_len=255)
        profile_url = _clean_text(
            mapped.get("profile_url") or mapped.get("url") or mapped.get("linkedin_url"),
            max_len=500,
        )
        summary = _clean_text(mapped.get("summary") or mapped.get("notes"), max_len=4000)
        skills_raw = mapped.get("skills") or mapped.get("skill") or ""
        skills = [part.strip() for part in re.split(r"[,|;]", skills_raw) if part.strip()][:40]
        open_to_work = _truthy(mapped.get("open_to_work") or mapped.get("looking_for_job"))
        if open_to_work and "open-to-work" not in {s.lower() for s in skills}:
            skills = ["open-to-work", *skills][:40]
        source_hint = mapped.get("source") or mapped.get("board")
        discovery_source, board_label = _infer_source(profile_url, source_hint)
        if board_label:
            prefix = f"Imported from recruiter export ({board_label})."
            summary = f"{summary} {prefix}".strip()[:4000] if summary else prefix
        confidence = 0.55
        if profile_url:
            confidence += 0.15
        if open_to_work:
            confidence += 0.1
        if company or location:
            confidence += 0.1
        rows.append(
            CsvImportRow(
                profile=PeopleProfile(
                    full_name=full_name,
                    headline=headline,
                    company=company,
                    location=location,
                    summary=summary,
                    skills=skills,
                    profile_url=profile_url or "",
                    confidence=round(min(confidence, 0.9), 2),
                    open_to_work=open_to_work,
                    credibility_score=0.6 if profile_url else 0.35,
                ),
                source=discovery_source,
                board_label=board_label,
            )
        )
    if not rows:
        raise CsvImportError("no_results", "No valid candidate rows found in the CSV.")
    return rows
