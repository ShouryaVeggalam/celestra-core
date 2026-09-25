"""Public GitHub people search for open-to-work talent."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import quote_plus

import httpx

GITHUB_API = "https://api.github.com"
_EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
_PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
_STOP = frozenset({"in", "a", "an", "the", "for", "with", "and", "or", "to", "of", "at"})
_OPEN_TO_WORK_RE = re.compile(
    r"(open[\s-]?to[\s-]?work|#opentowork|looking for (a |new )?job|"
    r"looking for opportunit|available for hire|open to opportunit|"
    r"seeking opportunit|actively looking|hire me)",
    re.IGNORECASE,
)
_OPEN_TO_WORK_SEARCH = (
    '("open to work" OR "looking for opportunities" OR '
    '"available for hire" OR "open to opportunities" OR #OpenToWork)'
)
MIN_ACCOUNT_AGE_DAYS = 90
MIN_PUBLIC_REPOS = 1
MIN_FOLLOWERS = 1
SEARCH_OVERSAMPLE = 4


class PeopleSearchError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


@dataclass(frozen=True)
class PeopleProfile:
    full_name: str
    headline: Optional[str]
    company: Optional[str]
    location: Optional[str]
    summary: Optional[str]
    skills: list[str]
    profile_url: str
    confidence: float
    open_to_work: bool = False
    credibility_score: float = 0.0


def _clean_text(value: Optional[str], *, max_len: int) -> Optional[str]:
    if not value or not str(value).strip():
        return None
    text = _EMAIL_RE.sub("", str(value).strip())
    text = _PHONE_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len] if text else None


def parse_query(query: str) -> tuple[str, Optional[str], list[str]]:
    cleaned = query.strip()
    location: Optional[str] = None
    if re.search(r"\bin\b", cleaned, re.I):
        head, tail = re.split(r"\bin\b", cleaned, maxsplit=1, flags=re.I)
        location = tail.strip() or None
        keywords_raw = head
    else:
        keywords_raw = cleaned
    tokens = [
        token.strip(".,;:!?")
        for token in re.split(r"\s+", keywords_raw)
        if token and token.lower() not in _STOP
    ]
    keywords = " ".join(tokens).strip() or cleaned
    return keywords, location, tokens


def build_github_search_q(query: str, *, job_seekers: bool = True) -> str:
    keywords, location, _tokens = parse_query(query)
    parts = [keywords, "type:user"]
    if job_seekers:
        parts.append(_OPEN_TO_WORK_SEARCH)
    if location:
        parts.append(f"location:{location}")
    return " ".join(parts)


def _parse_created_at(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _account_age_days(created_at: Optional[datetime]) -> Optional[int]:
    if created_at is None:
        return None
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return max(0, (now - created_at).days)


def _is_open_to_work(detail: dict[str, Any]) -> bool:
    if detail.get("hireable") is True:
        return True
    haystack = " ".join(str(detail.get(key) or "") for key in ("bio", "company", "blog", "twitter_username"))
    return bool(_OPEN_TO_WORK_RE.search(haystack))


def _is_credible(detail: dict[str, Any]) -> bool:
    if detail.get("type") == "Organization":
        return False
    age_days = _account_age_days(_parse_created_at(detail.get("created_at")))
    if age_days is None or age_days < MIN_ACCOUNT_AGE_DAYS:
        return False
    public_repos = int(detail.get("public_repos") or 0)
    followers = int(detail.get("followers") or 0)
    if public_repos < MIN_PUBLIC_REPOS and followers < MIN_FOLLOWERS:
        return False
    return True


def _credibility_score(detail: dict[str, Any], *, open_to_work: bool) -> float:
    age_days = _account_age_days(_parse_created_at(detail.get("created_at"))) or 0
    public_repos = int(detail.get("public_repos") or 0)
    followers = int(detail.get("followers") or 0)
    score = 0.2
    if open_to_work:
        score += 0.25
    if age_days >= 365:
        score += 0.2
    elif age_days >= MIN_ACCOUNT_AGE_DAYS:
        score += 0.1
    if public_repos >= 5:
        score += 0.15
    elif public_repos >= MIN_PUBLIC_REPOS:
        score += 0.08
    if followers >= 20:
        score += 0.15
    elif followers >= MIN_FOLLOWERS:
        score += 0.08
    if detail.get("bio"):
        score += 0.05
    return round(min(score, 0.98), 2)


def _confidence(*, name: str, location: Optional[str], company: Optional[str], summary: Optional[str], credibility: float, open_to_work: bool) -> float:
    score = 0.25
    if name and name.lower() not in {"unknown", "user"}:
        score += 0.15
    if location:
        score += 0.1
    if company:
        score += 0.1
    if summary:
        score += 0.1
    if open_to_work:
        score += 0.1
    score += credibility * 0.2
    return round(min(score, 0.95), 2)


def _headers(token: Optional[str]) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "hiring-ai-talent-sourcing",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _map_user(
    detail: dict[str, Any],
    *,
    skill_tokens: list[str],
    require_open_to_work: bool,
    force_open_to_work: bool = False,
) -> Optional[PeopleProfile]:
    if not _is_credible(detail):
        return None
    open_to_work = force_open_to_work or _is_open_to_work(detail)
    if require_open_to_work and not open_to_work:
        return None
    login = str(detail.get("login") or "").strip()
    html_url = str(detail.get("html_url") or "").strip()
    if not login or not html_url:
        return None
    display = _clean_text(detail.get("name"), max_len=255) or login
    company = _clean_text(detail.get("company"), max_len=255)
    if company:
        company = company.lstrip("@")
    location = _clean_text(detail.get("location"), max_len=255)
    bio = _clean_text(detail.get("bio"), max_len=4000)
    headline = _clean_text(detail.get("name"), max_len=500) or f"GitHub @{login}"[:500]
    skills = [token for token in skill_tokens if len(token) > 1][:38]
    if open_to_work and "open-to-work" not in {s.lower() for s in skills}:
        skills = ["open-to-work", *skills][:40]
    credibility = _credibility_score(detail, open_to_work=open_to_work)
    summary_bits = []
    if bio:
        summary_bits.append(bio)
    summary_bits.append(
        "Public profile signals open to work." if open_to_work else "Credible public GitHub profile."
    )
    return PeopleProfile(
        full_name=display,
        headline=headline,
        company=company,
        location=location,
        summary=" ".join(summary_bits)[:4000],
        skills=skills,
        profile_url=html_url[:500],
        confidence=_confidence(
            name=display,
            location=location,
            company=company,
            summary=bio,
            credibility=credibility,
            open_to_work=open_to_work,
        ),
        open_to_work=open_to_work,
        credibility_score=credibility,
    )


async def _search_logins(http: httpx.AsyncClient, *, search_q: str, fetch_count: int, token: Optional[str]) -> list[str]:
    search_url = f"{GITHUB_API}/search/users?q={quote_plus(search_q)}&per_page={fetch_count}"
    search_response = await http.get(search_url, headers=_headers(token))
    if search_response.status_code == 403:
        raise PeopleSearchError("rate_limited", "GitHub rate limit reached. Set GITHUB_TOKEN and try again.")
    if search_response.status_code >= 400:
        raise PeopleSearchError("people_search_unavailable", "Public people search is temporarily unavailable.")
    payload = search_response.json()
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        raise PeopleSearchError("people_search_unavailable", "Unexpected people search response.")
    logins: list[str] = []
    seen: set[str] = set()
    for item in items:
        login = str((item or {}).get("login") or "").strip()
        if not login or login in seen:
            continue
        seen.add(login)
        logins.append(login)
    return logins


async def search_github_people(
    query: str,
    *,
    limit: int,
    token: Optional[str] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> list[PeopleProfile]:
    limit = max(1, min(int(limit), 50))
    fetch_count = min(50, max(limit * SEARCH_OVERSAMPLE, limit))
    keywords, _location, skill_tokens = parse_query(query)
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=20.0)
    try:
        seeker_q = build_github_search_q(query, job_seekers=True)
        broad_q = build_github_search_q(query, job_seekers=False)
        logins = await _search_logins(http, search_q=seeker_q, fetch_count=fetch_count, token=token)
        seeker_login_set = set(logins)
        if len(logins) < fetch_count:
            for login in await _search_logins(http, search_q=broad_q, fetch_count=fetch_count, token=token):
                if login not in seeker_login_set:
                    logins.append(login)
                if len(logins) >= fetch_count:
                    break
        profiles: list[PeopleProfile] = []
        for login in logins:
            if len(profiles) >= limit:
                break
            detail_response = await http.get(f"{GITHUB_API}/users/{quote_plus(login)}", headers=_headers(token))
            if detail_response.status_code == 403:
                raise PeopleSearchError("rate_limited", "GitHub rate limit reached. Set GITHUB_TOKEN and try again.")
            if detail_response.status_code >= 400:
                continue
            detail = detail_response.json()
            if not isinstance(detail, dict):
                continue
            from_seeker = login in seeker_login_set
            mapped = _map_user(
                detail,
                skill_tokens=skill_tokens or keywords.split(),
                require_open_to_work=not from_seeker,
                force_open_to_work=from_seeker,
            )
            if mapped is not None:
                profiles.append(mapped)
        profiles.sort(key=lambda p: (p.open_to_work, p.credibility_score, p.confidence), reverse=True)
        return profiles[:limit]
    finally:
        if owns_client:
            await http.aclose()
