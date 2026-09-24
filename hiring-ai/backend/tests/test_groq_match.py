"""Groq match + structure tests (mocked HTTP)."""

from app.ai.groq_client import GroqClient, extract_json_object
from app.config import Settings
from tests.conftest import auth_headers


def test_extract_json_object_from_fence():
    payload = extract_json_object('```json\n{"score": 0.8, "summary": "ok"}\n```')
    assert payload["score"] == 0.8


def test_match_requires_groq_key(client, user_a, org_a):
    headers = auth_headers(user_a.id, org_a.id)
    job = client.post("/api/v1/jobs", headers=headers, json={"title": "Engineer"}).json()
    cand = client.post(
        "/api/v1/candidates",
        headers=headers,
        json={"first_name": "Ada", "last_name": "Lovelace"},
    ).json()
    response = client.post(
        "/api/v1/matches",
        headers=headers,
        json={"job_id": job["id"], "candidate_id": cand["id"]},
    )
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "groq_not_configured"


def test_match_uses_groq(client, user_a, org_a, monkeypatch):
    from app.config import get_settings

    settings = Settings(
        database_url="sqlite+pysqlite:///:memory:",
        auth_mode="dev",
        groq_api_key="gsk_test",
        groq_model="llama-3.3-70b-versatile",
        seed_demo_tenant=False,
        invite_code_pepper="test-pepper-not-for-prod",
    )
    client.app.dependency_overrides[get_settings] = lambda: settings
    monkeypatch.setattr("app.matching.router.get_settings", lambda: settings)

    async def fake_chat_json(self, *, system, user, temperature=0.2, max_tokens=2048):  # noqa: ARG001
        return {
            "score": 0.82,
            "summary": "Strong Python overlap for the role.",
            "strengths": ["Python", "API design"],
            "gaps": ["Cloud ops depth"],
            "evidence": ["Candidate skills include python"],
        }

    monkeypatch.setattr(GroqClient, "chat_json", fake_chat_json)

    headers = auth_headers(user_a.id, org_a.id)
    job = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={"title": "Backend Engineer", "description": "Python FastAPI"},
    ).json()
    cand = client.post(
        "/api/v1/candidates",
        headers=headers,
        json={
            "first_name": "Ada",
            "last_name": "Lovelace",
            "headline": "Python engineer",
            "skills": ["python", "fastapi"],
        },
    ).json()
    response = client.post(
        "/api/v1/matches",
        headers=headers,
        json={"job_id": job["id"], "candidate_id": cand["id"]},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["score"] == 0.82
    assert "Python" in body["strengths"][0] or "python" in body["strengths"][0].lower()
    assert body["model"] == "llama-3.3-70b-versatile"


def test_structure_job_via_groq(client, user_a, org_a, monkeypatch):
    from app.config import get_settings

    settings = Settings(
        database_url="sqlite+pysqlite:///:memory:",
        auth_mode="dev",
        groq_api_key="gsk_test",
        seed_demo_tenant=False,
        invite_code_pepper="test-pepper-not-for-prod",
    )
    client.app.dependency_overrides[get_settings] = lambda: settings
    monkeypatch.setattr("app.matching.router.get_settings", lambda: settings)

    async def fake_chat_json(self, *, system, user, temperature=0.2, max_tokens=2048):  # noqa: ARG001
        return {
            "title": "Staff Platform Engineer",
            "department": "Engineering",
            "location": "Remote",
            "description": "Build hiring infrastructure.",
        }

    monkeypatch.setattr(GroqClient, "chat_json", fake_chat_json)
    response = client.post(
        "/api/v1/ai/structure-job",
        headers=auth_headers(user_a.id, org_a.id),
        json={"text": "We need a Staff Platform Engineer in Engineering, remote, to build hiring infra."},
    )
    assert response.status_code == 200, response.text
    assert response.json()["title"] == "Staff Platform Engineer"
