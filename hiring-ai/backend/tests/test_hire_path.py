"""End-to-end hire path: job -> discover/CSV -> import -> hire."""

from io import BytesIO

from app.models import Candidate, CandidateStatus, Job
from tests.conftest import auth_headers


def test_job_candidate_and_csv_import_hire_path(client, user_a, org_a, db, monkeypatch):
    headers = auth_headers(user_a.id, org_a.id)

    job = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={"title": "Backend Engineer", "location": "Hyderabad"},
    )
    assert job.status_code == 200, job.text
    job_id = job.json()["id"]

    project = client.post(
        "/api/v1/source/projects",
        headers=headers,
        json={"name": "Backend seekers", "job_id": job_id},
    )
    assert project.status_code == 200, project.text
    project_id = project.json()["id"]

    csv = (
        "full_name,headline,company,location,profile_url,skills,open_to_work,source,email\n"
        "Riya Sharma,Backend Engineer,Acme,Hyderabad,https://github.com/riya,python|fastapi,yes,github,riya@example.com\n"
    )
    imported = client.post(
        f"/api/v1/source/projects/{project_id}/import-csv",
        headers=headers,
        files={"file": ("board.csv", BytesIO(csv.encode("utf-8")), "text/csv")},
    )
    assert imported.status_code == 200, imported.text
    discoveries = imported.json()["discoveries"]
    assert len(discoveries) == 1
    discovery_id = discoveries[0]["id"]
    assert "open-to-work" in discoveries[0]["skills"]
    assert "email" not in discoveries[0]

    # Before import: no candidates
    listed = client.get("/api/v1/candidates", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] == 0

    result = client.post(f"/api/v1/source/import/{discovery_id}", headers=headers)
    assert result.status_code == 200, result.text
    candidate_id = result.json()["candidate_id"]
    assert result.json()["discovery"]["status"] == "imported"

    listed = client.get("/api/v1/candidates", headers=headers)
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == candidate_id

    hired = client.post(
        f"/api/v1/candidates/{candidate_id}/status",
        headers=headers,
        json={"status": "hired"},
    )
    assert hired.status_code == 200
    assert hired.json()["status"] == "hired"

    db.expire_all()
    cand = db.get(Candidate, candidate_id)
    assert cand is not None
    assert cand.status == CandidateStatus.HIRED
    assert db.get(Job, job_id) is not None


def test_discover_persists_github_profiles(client, user_a, org_a, monkeypatch):
    async def fake_search(query, *, limit, token=None, client=None):
        del query, token, client
        from app.talent_sourcing.people_search import PeopleProfile

        return [
            PeopleProfile(
                full_name="Ada Example",
                headline="Staff Engineer",
                company="Labs",
                location="Hyderabad",
                summary="Public profile signals open to work.",
                skills=["open-to-work", "python"],
                profile_url="https://github.com/ada-example",
                confidence=0.8,
                open_to_work=True,
                credibility_score=0.7,
            )
        ][:limit]

    monkeypatch.setattr("app.talent_sourcing.service.search_github_people", fake_search)
    headers = auth_headers(user_a.id, org_a.id)
    project = client.post("/api/v1/source/projects", headers=headers, json={"name": "GH"})
    project_id = project.json()["id"]
    response = client.post(
        "/api/v1/source/discover",
        headers=headers,
        json={"project_id": project_id, "query": "python in hyderabad", "limit": 5},
    )
    assert response.status_code == 200, response.text
    item = response.json()["discoveries"][0]
    assert item["full_name"] == "Ada Example"
    assert item["source"] == "github"
    assert "open-to-work" in item["skills"]
