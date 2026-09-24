"""Public people search helpers."""

from app.talent_sourcing.people_search import build_github_search_q, parse_query


def test_build_search_prefers_open_to_work_phrases():
    keywords, location, tokens = parse_query("python engineer in hyderabad")
    assert "python" in keywords.lower()
    assert location == "hyderabad"
    assert "python" in tokens
    q = build_github_search_q("python engineer in hyderabad", job_seekers=True)
    assert "open to work" in q
    assert "location:hyderabad" in q
    assert "hireable:true" not in q
