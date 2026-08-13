"""Settings validation and configuration manager."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.environment import Environment, load_environment


class Settings(BaseSettings):
    """Validated platform configuration."""

    model_config = SettingsConfigDict(
        env_prefix="CELESTRA_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: Environment = Environment.DEVELOPMENT
    app_name: str = "celestra-core"
    debug: bool = False
    api_prefix: str = "/api/v1"
    secret_key: str = Field(default="dev-only-change-me", min_length=8)

    # --- Auth / JWT ---
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, ge=1, le=24 * 60)
    jwt_refresh_token_expire_days: int = Field(default=14, ge=1, le=365)
    auth_allow_registration: bool = True
    auth_default_role: str = "member"

    # --- Identity bridge (product → Core token exchange) ---
    # HMAC secret shared with product backends for signed user assertions (never expose to FE).
    bridge_assertion_secret: str | None = None
    # Legacy single issuer (Revenue default). Prefer bridge_issuers for multi-product.
    bridge_issuer: str = "revenue-ai"
    # Per-application expected iss claim: "revenue=revenue-ai,hiring=hiring-ai,..."
    bridge_issuers: dict[str, str] = Field(default_factory=dict)
    bridge_audience: str = "celestra-core"
    bridge_clock_skew_seconds: int = Field(default=60, ge=0, le=300)
    bridge_jti_ttl_seconds: int = Field(default=300, ge=30, le=3600)
    bridge_access_token_expire_seconds: int = Field(default=300, ge=60, le=3600)
    bridge_token_issuer: str = "celestra-core"
    bridge_token_audience: str = "celestra-core"

    # --- Monitoring ---
    metrics_enabled: bool = True
    metrics_namespace: str = "celestra"
    # When true, GET /ready runs SELECT 1 against the DB (default off — conservative).
    ready_check_db: bool = False
    # Slow-request log threshold for PerformanceMiddleware (milliseconds).
    slow_request_ms: float = Field(default=1000.0, ge=1.0, le=600_000.0)

    # --- AI / Providers ---
    ai_default_provider: str = "mock"
    ai_default_model: str = "mock-chat"
    ai_timeout_seconds: float = Field(default=60.0, ge=1.0, le=600.0)
    ai_max_retries: int = Field(default=2, ge=0, le=5)
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_default_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    anthropic_api_key: str | None = None
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_default_model: str = "claude-3-5-sonnet-20241022"

    # --- Memory / Agents / Workflows (Phase 4) ---
    memory_window_size: int = Field(default=20, ge=1, le=500)
    agent_max_steps_default: int = Field(default=5, ge=1, le=25)
    workflow_celery_enabled: bool = False

    # --- Storage / Notifications / Knowledge (Phase 5) ---
    storage_backend: Literal["local", "memory", "s3"] = "local"
    storage_local_path: str = ".data/storage"
    storage_bucket: str = "celestra"
    s3_endpoint_url: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_region: str = "us-east-1"
    knowledge_chunk_size: int = Field(default=800, ge=100, le=8000)
    knowledge_chunk_overlap: int = Field(default=100, ge=0, le=2000)

    # --- Billing / Analytics / SDK (Phase 6) ---
    billing_default_plan: str = "free"

    # --- Production hardening (Phase 7) ---
    # Conversation backend: "memory" (process-local) or "redis" (shared, fail-closed).
    # When set to redis, startup requires a reachable Redis — no silent in-memory fallback.
    # TTL is refreshed on every save/append; expired keys are removed by Redis.
    memory_conversation_backend: Literal["memory", "redis"] = "memory"
    memory_conversation_ttl_seconds: int = Field(default=60 * 60 * 24 * 7, ge=60)
    # Vector/RAG store — NOT multi-user scoped; do not enable for multi-tenant prod.
    memory_vector_backend: Literal["memory", "postgres"] = "memory"
    workflow_run_backend: Literal["memory", "redis"] = "memory"
    workflow_run_ttl_seconds: int = Field(default=60 * 60 * 24 * 30, ge=60)
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True
    stripe_secret_key: str | None = None
    stripe_price_map: dict[str, str] = Field(default_factory=dict)
    oidc_issuer: str | None = None
    oidc_client_id: str | None = None
    oidc_client_secret: str | None = None
    oidc_redirect_uri: str | None = None
    oidc_scopes: list[str] = Field(default_factory=lambda: ["openid", "profile", "email"])

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    database_url: str = "postgresql+asyncpg://celestra:celestra@localhost:5432/celestra_core"
    database_url_sync: str = "postgresql+psycopg2://celestra:celestra@localhost:5432/celestra_core"
    db_pool_size: int = Field(default=5, ge=1, le=100)
    db_max_overflow: int = Field(default=10, ge=0, le=100)
    db_echo: bool = False

    redis_url: str = "redis://localhost:6379/0"
    redis_prefix: str = "celestra:"
    cache_default_ttl: int = Field(default=300, ge=1)
    lock_default_ttl: int = Field(default=30, ge=1)

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_json: bool = True
    log_requests: bool = True
    log_performance: bool = True

    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"]
    )

    @field_validator("cors_origins", "oidc_scopes", mode="before")
    @classmethod
    def parse_string_list(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                import json
                return json.loads(stripped)
            return [part.strip() for part in stripped.split(",") if part.strip()]
        return value

    @field_validator("bridge_issuers", mode="before")
    @classmethod
    def parse_bridge_issuers(cls, value: object) -> object:
        if value is None:
            return {}
        if isinstance(value, dict):
            return {str(k).strip().lower(): str(v).strip() for k, v in value.items() if str(k).strip()}
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return {}
            if stripped.startswith("{"):
                import json
                raw = json.loads(stripped)
                return {str(k).strip().lower(): str(v).strip() for k, v in raw.items()}
            mapping: dict[str, str] = {}
            for part in stripped.split(","):
                if "=" not in part:
                    continue
                app, issuer = part.split("=", 1)
                app = app.strip().lower()
                issuer = issuer.strip()
                if app and issuer:
                    mapping[app] = issuer
            return mapping
        return value

    @field_validator("stripe_price_map", mode="before")
    @classmethod
    def parse_stripe_price_map(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return {}
            if stripped.startswith("{"):
                import json
                return json.loads(stripped)
            mapping: dict[str, str] = {}
            for part in stripped.split(","):
                if "=" not in part:
                    continue
                plan_id, price_id = part.split("=", 1)
                mapping[plan_id.strip()] = price_id.strip()
            return mapping
        return value

    @model_validator(mode="after")
    def enforce_production_guards(self) -> Settings:
        if self.env is Environment.PRODUCTION:
            weak = {"dev-only-change-me", "change-me-in-production-use-openssl-rand-hex-32"}
            if self.secret_key in weak:
                raise ValueError("CELESTRA_SECRET_KEY must be set to a strong value in production")
            if self.debug:
                raise ValueError("CELESTRA_DEBUG must be false in production")
        return self

    @property
    def is_production(self) -> bool:
        return self.env is Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.env is Environment.DEVELOPMENT

    @property
    def is_test(self) -> bool:
        return self.env is Environment.TEST

    def bridge_issuer_map(self) -> dict[str, str]:
        """Resolved application → expected assertion issuer."""
        from config.applications import DEFAULT_BRIDGE_ISSUERS

        merged = dict(DEFAULT_BRIDGE_ISSUERS)
        # Legacy single issuer applies to revenue when map omits it.
        if self.bridge_issuer:
            merged.setdefault("revenue", self.bridge_issuer)
        merged.update(self.bridge_issuers)
        return merged


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Configuration manager singleton."""
    load_environment()
    return Settings()


def clear_settings_cache() -> None:
    """Invalidate the cached Settings instance (used by tests)."""
    get_settings.cache_clear()
