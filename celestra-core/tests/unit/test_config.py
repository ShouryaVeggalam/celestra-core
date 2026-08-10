"""Unit tests — configuration."""

from config.environment import Environment
from config.secrets import DictSecretProvider, EnvSecretProvider
from config.settings import Settings, clear_settings_cache


def test_environment_aliases():
    assert Environment.from_value("dev") is Environment.DEVELOPMENT
    assert Environment.from_value("prod") is Environment.PRODUCTION
    assert Environment.from_value("stage") is Environment.STAGING


def test_settings_defaults(monkeypatch):
    clear_settings_cache()
    monkeypatch.setenv("CELESTRA_ENV", "test")
    monkeypatch.setenv("CELESTRA_SECRET_KEY", "test-secret-key-not-for-prod")
    settings = Settings()
    assert settings.app_name == "celestra-core"
    assert settings.is_test
    assert settings.cache_default_ttl == 300
    clear_settings_cache()


def test_production_rejects_weak_secret(monkeypatch):
    clear_settings_cache()
    monkeypatch.setenv("CELESTRA_ENV", "production")
    monkeypatch.setenv("CELESTRA_SECRET_KEY", "dev-only-change-me")
    monkeypatch.setenv("CELESTRA_DEBUG", "false")
    try:
        raised = False
        try:
            Settings()
        except Exception:
            raised = True
        assert raised
    finally:
        clear_settings_cache()


def test_dict_secret_provider():
    provider = DictSecretProvider({"CELESTRA_SECRET_KEY": "abc"})
    assert provider.require("CELESTRA_SECRET_KEY") == "abc"
    assert provider.get("missing", "fallback") == "fallback"


def test_env_secret_provider(monkeypatch):
    monkeypatch.setenv("DEMO_SECRET", "value")
    provider = EnvSecretProvider()
    assert provider.get("DEMO_SECRET") == "value"
