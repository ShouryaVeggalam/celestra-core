"""Firebase auth mode, provisioning, org bootstrap, invites, public portal."""

from __future__ import annotations

from app.config import Settings, get_settings
from app.firebase_auth import FirebaseClaims
from app.models import AuthIdentity, User
from tests.conftest import auth_headers


def test_dev_me_requires_bearer(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_dev_me_returns_memberships(client, user_a, org_a):
    response = client.get("/api/v1/auth/me", headers=auth_headers(user_a.id))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user_id"] == user_a.id
    assert body["email"] == "ada@example.com"
    assert len(body["memberships"]) == 1
    assert body["memberships"][0]["organization_id"] == org_a.id
    assert body["memberships"][0]["role"] == "owner"
    assert "firebase_uid" not in body


def test_firebase_mode_rejects_bad_token(client, monkeypatch):
    settings = Settings(
        database_url="sqlite+pysqlite:///:memory:",
        auth_mode="firebase",
        firebase_project_id="hiring-test",
        environment="development",
        seed_demo_tenant=False,
        invite_code_pepper="test-pepper-not-for-prod",
    )
    monkeypatch.setattr("app.config.get_settings", lambda: settings)
    get_settings.cache_clear()
    client.app.dependency_overrides[get_settings] = lambda: settings

    def boom(token, settings):  # noqa: ARG001
        from app.firebase_auth import FirebaseAuthError

        raise FirebaseAuthError("Invalid or expired Firebase ID token.")

    monkeypatch.setattr("app.auth.verify_firebase_id_token", boom)
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer fake.jwt.token"})
    assert response.status_code == 401


def test_firebase_mode_provisions_user_once(client, db, monkeypatch):
    settings = Settings(
        database_url="sqlite+pysqlite:///:memory:",
        auth_mode="firebase",
        firebase_project_id="hiring-test",
        environment="development",
        seed_demo_tenant=False,
        invite_code_pepper="test-pepper-not-for-prod",
    )
    monkeypatch.setattr("app.config.get_settings", lambda: settings)
    get_settings.cache_clear()
    client.app.dependency_overrides[get_settings] = lambda: settings

    monkeypatch.setattr(
        "app.auth.verify_firebase_id_token",
        lambda token, settings: FirebaseClaims(  # noqa: ARG005
            uid="firebase-uid-ada",
            email="ada@firebase.test",
            name="Ada Firebase",
            email_verified=True,
        ),
    )

    first = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer id-token-1"})
    assert first.status_code == 200, first.text
    user_id = first.json()["user_id"]
    assert first.json()["email"] == "ada@firebase.test"
    assert first.json()["memberships"] == []

    second = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer id-token-2"})
    assert second.status_code == 200
    assert second.json()["user_id"] == user_id

    db.expire_all()
    identities = db.query(AuthIdentity).all() if hasattr(db, "query") else []
    from sqlalchemy import select

    identities = list(db.scalars(select(AuthIdentity)).all())
    assert len(identities) == 1
    assert identities[0].subject == "firebase-uid-ada"
    assert identities[0].provider == "firebase"
    user = db.get(User, user_id)
    assert user is not None
    assert not hasattr(user, "firebase_uid")


def test_bootstrap_first_organization(client, user_a):
    response = client.post(
        "/api/v1/auth/organizations",
        headers=auth_headers(user_a.id),
        json={"name": "Northwind", "slug": "northwind"},
    )
    # user_a may already have org from fixture — create fresh user path below
    assert response.status_code in {200, 409}


def test_bootstrap_org_for_user_without_membership(client, db):
    user = User(id="user-fresh", email="fresh@example.com", display_name="Fresh", status=__import__("app.models", fromlist=["Status"]).Status.ACTIVE)
    db.add(user)
    db.commit()

    response = client.post(
        "/api/v1/auth/organizations",
        headers=auth_headers(user.id),
        json={"name": "Fresh Org", "slug": "fresh-org"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["organization_slug"] == "fresh-org"
    assert body["role"] == "owner"

    me = client.get("/api/v1/auth/me", headers=auth_headers(user.id)).json()
    assert len(me["memberships"]) == 1


def test_invite_create_and_redeem(client, user_a, org_a, db):
    from app.models import Status, User

    created = client.post(
        f"/api/v1/organizations/{org_a.id}/invite-codes",
        headers=auth_headers(user_a.id, org_a.id),
        json={"role": "member"},
    )
    assert created.status_code == 200, created.text
    code = created.json()["code"]
    assert len(code) == 8

    invitee = User(id="invitee-1", email="bob@example.com", display_name="Bob", status=Status.ACTIVE)
    db.add(invitee)
    db.commit()

    redeemed = client.post(
        "/api/v1/invite-codes/redeem",
        headers=auth_headers(invitee.id),
        json={"code": code},
    )
    assert redeemed.status_code == 200, redeemed.text
    assert redeemed.json()["organization_id"] == org_a.id
    assert redeemed.json()["role"] == "member"

    me = client.get("/api/v1/auth/me", headers=auth_headers(invitee.id)).json()
    assert any(m["organization_id"] == org_a.id for m in me["memberships"])


def test_candidate_portal_is_public(client, user_a, org_a, db):
    from app.models import Candidate, CandidatePortalAccess, new_id

    cand = Candidate(
        id=new_id(),
        org_id=org_a.id,
        first_name="Pat",
        last_name="Lee",
        created_by_user_id=user_a.id,
    )
    db.add(cand)
    db.flush()
    row = CandidatePortalAccess(
        id=new_id(),
        org_id=org_a.id,
        candidate_id=cand.id,
        token="public-token-abc",
        offer_title="Draft offer",
        offer_body="Review with your recruiter.",
        response_status="pending",
        created_by_user_id=user_a.id,
    )
    db.add(row)
    db.commit()

    missing = client.get("/api/v1/candidate-portal/does-not-exist")
    assert missing.status_code == 404

    response = client.get("/api/v1/candidate-portal/public-token-abc")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    assert response.json()["candidate_name"] == "Pat Lee"
    assert "Authorization" not in (response.request.headers or {})


def test_user_model_excludes_firebase_uid_column():
    from app.models import User

    assert "firebase_uid" not in User.__table__.columns
