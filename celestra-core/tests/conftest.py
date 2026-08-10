"""Shared pytest fixtures for Celestra Core."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CELESTRA_ENV", "test")
os.environ.setdefault("CELESTRA_SECRET_KEY", "test-secret-key-not-for-prod")
os.environ.setdefault("CELESTRA_DEBUG", "true")
os.environ.setdefault("CELESTRA_LOG_JSON", "false")
os.environ.setdefault("CELESTRA_LOG_REQUESTS", "false")
os.environ.setdefault("CELESTRA_LOG_PERFORMANCE", "false")


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch):
    from config.settings import Settings, clear_settings_cache

    clear_settings_cache()
    monkeypatch.setenv("CELESTRA_ENV", "test")
    yield Settings()
    clear_settings_cache()


@pytest.fixture
def app(settings):
    from contextlib import asynccontextmanager
    from typing import AsyncIterator

    from fastapi import FastAPI

    from core.container import build_container, reset_container
    from shared.exceptions.handlers import register_exception_handlers
    from shared.logging.setup import configure_logging

    @asynccontextmanager
    async def test_lifespan(application: FastAPI) -> AsyncIterator[None]:
        configure_logging(settings)
        build_container(settings)
        yield
        reset_container()

    application = FastAPI(title="celestra-core-test", lifespan=test_lifespan)
    application.state.settings = settings
    register_exception_handlers(application)

    @application.get("/health")
    async def health():
        return {"status": "ok", "app": settings.app_name, "env": settings.env.value}

    yield application
    reset_container()


@pytest.fixture
def client(app) -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
