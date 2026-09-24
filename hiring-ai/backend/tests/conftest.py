"""pytest fixtures for Hiring AI auth tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base, get_db
from app.main import create_app
from app.models import Membership, MembershipStatus, Organization, Role, Status, User, new_id


@pytest.fixture()
def settings(monkeypatch):
    s = Settings(
        database_url="sqlite+pysqlite:///:memory:",
        auth_mode="dev",
        environment="development",
        seed_demo_tenant=False,
        firebase_project_id="",
        invite_code_pepper="test-pepper-not-for-prod",
    )
    monkeypatch.setattr("app.config.get_settings", lambda: s)
    get_settings.cache_clear()
    yield s
    get_settings.cache_clear()


@pytest.fixture()
def db_engine(settings):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db(db_engine):
    Session = sessionmaker(bind=db_engine, autoflush=False, autocommit=False, future=True)
    session = Session()
    yield session
    session.close()


@pytest.fixture()
def client(db_engine, settings, monkeypatch):
    Session = sessionmaker(bind=db_engine, autoflush=False, autocommit=False, future=True)

    def _get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def user_a(db):
    user = User(id=new_id(), email="ada@example.com", display_name="Ada", status=Status.ACTIVE)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def org_a(db, user_a):
    org = Organization(id=new_id(), name="Acme Hiring", slug="acme-hiring", status=Status.ACTIVE)
    db.add(org)
    db.flush()
    db.add(
        Membership(
            id=new_id(),
            org_id=org.id,
            user_id=user_a.id,
            role=Role.OWNER,
            status=MembershipStatus.ACTIVE,
        )
    )
    db.commit()
    db.refresh(org)
    return org


def auth_headers(user_id: str, org_id: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {user_id}"}
    if org_id:
        headers["X-Organization-Id"] = org_id
    return headers
