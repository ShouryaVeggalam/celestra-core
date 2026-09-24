from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Hiring AI"
    environment: str = "development"
    version: str = "0.38.0"
    database_url: str = "sqlite+pysqlite:///./hiring_ai.db"
    auth_mode: str = "dev"  # dev | firebase
    firebase_project_id: str = ""
    cors_origins: str = "http://127.0.0.1:5177,http://localhost:5177"
    oauth_redirect_url: str = "http://127.0.0.1:5177/auth/callback"
    fernet_key: str = ""
    invite_code_pepper: str = "hiring-ai-invite-dev-pepper"
    seed_demo_tenant: bool = False
    hiring_complete_stub: bool = True
    talent_sourcing_provider: str = "github"
    github_token: str = ""
    celestra_core_enabled: bool = False
    celestra_core_url: str = ""
    celestra_core_api_key: str = ""
    celestra_bridge_assertion_secret: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [part.strip() for part in self.cors_origins.split(",") if part.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
