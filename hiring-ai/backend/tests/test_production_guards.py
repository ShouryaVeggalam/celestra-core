"""Production guard unit tests."""

import pytest

from app.config import Settings
from app.production_guards import ProductionGuardError, assert_hosted_safe


def test_dev_environment_skips_guards():
    assert_hosted_safe(
        Settings(environment="development", auth_mode="dev", database_url="sqlite+pysqlite:///./x.db")
    )


def test_hosted_refuses_dev_auth():
    with pytest.raises(ProductionGuardError, match="AUTH_MODE=dev"):
        assert_hosted_safe(
            Settings(
                environment="staging",
                auth_mode="dev",
                database_url="postgresql://u:p@db.example/hiring",
                firebase_project_id="proj",
                oauth_redirect_url="https://app.example/auth/callback",
                cors_origins="https://app.example",
                invite_code_pepper="a-very-long-unique-pepper-value",
                seed_demo_tenant=False,
            )
        )


def test_hosted_accepts_firebase():
    assert_hosted_safe(
        Settings(
            environment="staging",
            auth_mode="firebase",
            database_url="postgresql://u:p@db.example/hiring",
            firebase_project_id="proj",
            oauth_redirect_url="https://app.example/auth/callback",
            cors_origins="https://app.example",
            invite_code_pepper="a-very-long-unique-pepper-value",
            seed_demo_tenant=False,
        )
    )
