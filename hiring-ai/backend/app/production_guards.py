"""Refuse unsafe hosted configurations."""

from __future__ import annotations

from app.config import Settings
from app.health import database_engine_kind, is_localhost_postgres


PLACEHOLDER_PEPPERS = {
    "hiring-ai-invite-dev-pepper",
    "change-me",
    "replace-with-a-long-random-pepper",
}


class ProductionGuardError(RuntimeError):
    pass


def assert_hosted_safe(settings: Settings) -> None:
    env = (settings.environment or "").strip().lower()
    if env not in {"production", "staging"}:
        return

    if database_engine_kind(settings.database_url) != "postgresql":
        raise ProductionGuardError("Hosted environments require PostgreSQL.")
    if is_localhost_postgres(settings.database_url):
        raise ProductionGuardError("Hosted PostgreSQL must not use localhost.")
    if "*" in settings.cors_origins:
        raise ProductionGuardError("CORS must not use wildcard origins when hosted.")
    redirect = (settings.oauth_redirect_url or "").strip()
    if not redirect.startswith("https://"):
        raise ProductionGuardError("OAUTH_REDIRECT_URL must be HTTPS when hosted.")
    if not (settings.firebase_project_id or "").strip():
        raise ProductionGuardError("FIREBASE_PROJECT_ID is required when hosted.")
    if (settings.auth_mode or "").strip().lower() == "dev":
        raise ProductionGuardError("AUTH_MODE=dev is refused for design partners.")
    if (settings.invite_code_pepper or "").strip() in PLACEHOLDER_PEPPERS:
        raise ProductionGuardError("INVITE_CODE_PEPPER must not be a placeholder.")
    if settings.seed_demo_tenant:
        raise ProductionGuardError("SEED_DEMO_TENANT must be false when hosted.")
