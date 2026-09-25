"""Intelligence agents and feature-area API coverage (human-in-the-loop)."""

from __future__ import annotations

from app.models import Candidate, Job, JobStatus
from tests.conftest import auth_headers


def _seed_job_and_candidate(db, org_a, user_a):
    job = Job(
        id="job-agents-1",
        org_id=org_a.id,
        title="Platform Engineer",
        location="Remote",
        description="Build hiring systems",
        status=JobStatus.OPEN,
        created_by_user_id=user_a.id,
    )
    cand = Candidate(
        id="cand-agents-1",
        org_id=org_a.id,
        first_name="Riya",
        last_name="Sharma",
        headline="Backend Engineer",
        summary="Python FastAPI Nest",
        skills=["python", "fastapi"],
        created_by_user_id=user_a.id,
    )
    db.add_all([job, cand])
    db.commit()
    return job, cand


def test_reviews_and_analytics(client, user_a, org_a, db):
    headers = auth_headers(user_a.id, org_a.id)
    _seed_job_and_candidate(db, org_a, user_a)

    created = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={
            "candidate_id": "cand-agents-1",
            "job_id": "job-agents-1",
            "overall_score": 4.2,
            "recommendation": "advance",
            "notes": "Strong systems thinking",
            "scores": {"systems": 4.5},
        },
    )
    assert created.status_code == 200, created.text
    assert created.json()["overall_score"] == 4.2

    listed = client.get("/api/v1/reviews", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["items"][0]["recommendation"] == "advance"

    analytics = client.get("/api/v1/analytics/summary", headers=headers)
    assert analytics.status_code == 200
    body = analytics.json()
    assert body["open_jobs"] >= 1
    assert body["reviews"] >= 1


def test_interview_without_groq_uses_defaults(client, user_a, org_a, db, monkeypatch):
    headers = auth_headers(user_a.id, org_a.id)
    _seed_job_and_candidate(db, org_a, user_a)

    created = client.post(
        "/api/v1/interviews",
        headers=headers,
        json={
            "candidate_id": "cand-agents-1",
            "job_id": "job-agents-1",
            "title": "Screen",
            "generate_with_ai": False,
        },
    )
    assert created.status_code == 200, created.text
    assert len(created.json()["questions"]) >= 3

    listed = client.get("/api/v1/interviews", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["items"][0]["title"] == "Screen"


def test_referral_portal_integrations_without_ai(client, user_a, org_a, db):
    headers = auth_headers(user_a.id, org_a.id)
    _seed_job_and_candidate(db, org_a, user_a)

    referral = client.post(
        "/api/v1/referrals",
        headers=headers,
        json={
            "referrer_name": "Alex Manager",
            "candidate_name": "Jordan Dev",
            "job_id": "job-agents-1",
            "enrich_with_ai": False,
        },
    )
    assert referral.status_code == 200, referral.text
    assert referral.json()["status"] == "new"

    portal = client.post(
        "/api/v1/candidate-portal",
        headers=headers,
        json={"candidate_id": "cand-agents-1", "offer_title": "Draft offer"},
    )
    assert portal.status_code == 200, portal.text
    token = portal.json()["token"]

    public = client.get(f"/api/v1/candidate-portal/{token}")
    assert public.status_code == 200
    assert public.json()["status"] == "pending"
    assert public.json()["candidate_name"] == "Riya Sharma"

    respond = client.post(
        f"/api/v1/candidate-portal/{token}/respond",
        json={"response_status": "maybe", "response_note": "Need more time"},
    )
    assert respond.status_code == 200
    assert respond.json()["response_status"] == "maybe"

    integration = client.post(
        "/api/v1/integrations",
        headers=headers,
        json={"provider": "Greenhouse", "notes": "Sandbox"},
    )
    assert integration.status_code == 200
    assert integration.json()["provider"] == "greenhouse"

    listed = client.get("/api/v1/integrations", headers=headers)
    assert listed.status_code == 200
    assert any(item["provider"] == "greenhouse" for item in listed.json()["items"])
    assert any(item["provider"] == "groq" for item in listed.json()["builtins"])


def test_agent_drafts_with_mocked_groq(client, user_a, org_a, db, monkeypatch, settings):
    headers = auth_headers(user_a.id, org_a.id)
    _seed_job_and_candidate(db, org_a, user_a)

    async def fake_chat_json(self, *, system, user, temperature=0.2, max_tokens=2048):
        del self, system, user, temperature, max_tokens
        return {
            "subject": "Hello Riya",
            "body": "We liked your profile.",
            "tone": "warm",
            "core_skills": ["python"],
            "adjacent_skills": ["go"],
            "evidence": ["FastAPI work"],
            "gaps": [],
            "currency": "USD",
            "low": 100000,
            "mid": 130000,
            "high": 160000,
            "rationale": "Market mid",
            "caveats": ["Advisory only"],
            "outlook": "Healthy pipeline",
            "risks": [],
            "recommended_actions": ["Source more seniors"],
            "title": "Engineering hire playbook",
            "stages": [{"name": "Screen", "checklist": ["Resume"]}],
            "guardrails": ["Human hire only"],
            "priorities": ["Fill platform role"],
            "executive_summary": "Focus platform hire",
            "tasks": [{"title": "Prep scorecard", "rationale": "Ready reviewers"}],
            "body_markdown": "# Brief\nHire carefully.",
            "fit_notes": "Good cultural fit signal",
            "screening_questions": ["Why us?"],
            "risk_flags": [],
            "questions": ["Tell me about a distributed system you built."],
            "summary": "Strong backend signal",
        }

    monkeypatch.setattr(settings, "groq_api_key", "test-key-for-agents")
    monkeypatch.setattr("app.ai.groq_client.GroqClient.chat_json", fake_chat_json)

    outreach = client.post(
        "/api/v1/agents/outreach",
        headers=headers,
        json={"candidate_id": "cand-agents-1", "job_id": "job-agents-1"},
    )
    assert outreach.status_code == 200, outreach.text
    assert outreach.json()["kind"] == "outreach"

    skills = client.post(
        "/api/v1/agents/skills",
        headers=headers,
        json={"candidate_id": "cand-agents-1"},
    )
    assert skills.status_code == 200, skills.text

    comp = client.post(
        "/api/v1/agents/compensation",
        headers=headers,
        json={"job_id": "job-agents-1"},
    )
    assert comp.status_code == 200, comp.text

    forecast = client.post("/api/v1/agents/forecast", headers=headers, json={"topic": "Q4"})
    assert forecast.status_code == 200, forecast.text

    playbook = client.post(
        "/api/v1/agents/playbooks",
        headers=headers,
        json={"topic": "Eng hire"},
    )
    assert playbook.status_code == 200, playbook.text

    chief = client.post("/api/v1/agents/hiring-chief", headers=headers, json={})
    assert chief.status_code == 200, chief.text

    prep = client.post("/api/v1/agents/autonomous-prep", headers=headers, json={})
    assert prep.status_code == 200, prep.text
    tasks = prep.json()["payload"]["tasks"]
    assert tasks[0]["requires_human"] is True
    assert tasks[0]["auto_execute"] is False

    doc = client.post(
        "/api/v1/documents",
        headers=headers,
        json={"doc_type": "hiring_brief", "job_id": "job-agents-1"},
    )
    assert doc.status_code == 200, doc.text

    artifacts = client.get("/api/v1/agents/artifacts", headers=headers)
    assert artifacts.status_code == 200
    assert len(artifacts.json()["items"]) >= 5
