"""Health and readiness probes."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings


def firebase_configured(settings: Settings) -> bool:
    return bool((settings.firebase_project_id or "").strip())


def is_localhost_postgres(url: str) -> bool:
    lowered = (url or "").lower()
    return "localhost" in lowered or "127.0.0.1" in lowered


def database_engine_kind(url: str) -> str:
    if (url or "").startswith("sqlite"):
        return "sqlite"
    if "postgres" in (url or "").lower():
        return "postgresql"
    return "unknown"


def build_health(settings: Settings) -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "hiring-ai",
        "application": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
    }


def build_ready(settings: Settings, db: Session, *, migrations_at_head: bool = True) -> tuple[int, dict[str, Any]]:
    hosted = settings.environment.lower() in {"production", "staging"}
    engine = database_engine_kind(settings.database_url)
    database_ok = False
    try:
        db.execute(text("SELECT 1"))
        database_ok = True
    except Exception:  # noqa: BLE001
        database_ok = False

    if hosted:
        database_ok = (
            database_ok
            and engine == "postgresql"
            and not is_localhost_postgres(settings.database_url)
        )

    firebase_ok = firebase_configured(settings)
    firebase_ready = firebase_ok if hosted else True
    ready = database_ok and firebase_ready and bool(migrations_at_head)
    groq_ok = bool((settings.groq_api_key or "").strip())

    payload = {
        "status": "ready" if ready else "not_ready",
        "service": "hiring-ai",
        "environment": settings.environment,
        "version": settings.version,
        "database": "ok" if database_ok else "unavailable",
        "firebase": "ok" if firebase_ok else "unavailable",
        "groq": "ok" if groq_ok else "unavailable",
        "celestra_core": "disabled" if not settings.celestra_core_enabled else "ok",
    }
    return (200 if ready else 503, payload)
