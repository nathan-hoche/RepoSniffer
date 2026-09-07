from __future__ import annotations

from reposniffer.engine.github import build_search_query, excerpt, strip_markdown
from reposniffer.engine.score import activity_score, combine_score, quality_score


def test_build_search_query_adds_filters():
    q = build_search_query("markdown editor", language="python", license_key="mit", min_stars=100)
    assert "markdown editor" in q
    assert "language:python" in q
    assert "license:mit" in q
    assert "stars:>=100" in q
    assert "archived:false" in q


def test_build_search_query_includes_archived_when_requested():
    q = build_search_query("x", include_archived=True)
    assert "archived:false" not in q


def test_strip_markdown():
    assert strip_markdown("**bold** `code` [link](http://x)") == "bold code link"
    assert strip_markdown("```py\nx=1\n```") == ""


def test_excerpt_truncates():
    assert len(excerpt("a" * 1000)) <= 500


def test_activity_score_decays():
    fresh = activity_score("2026-09-06T12:00:00Z")
    old = activity_score("2020-01-01T12:00:00Z")
    assert fresh > 0.9
    assert old < fresh


def test_archived_penalizes_quality():
    active = {
        "stargazers_count": 100,
        "forks_count": 10,
        "pushed_at": "2026-08-01T12:00:00Z",
        "license": {"spdx_id": "MIT"},
        "archived": False,
    }
    archived = {**active, "archived": True}
    q1 = quality_score(active)["quality"]
    q2 = quality_score(archived)["quality"]
    assert q2 < q1


def test_combine_score_weights():
    adopt = combine_score(1.0, 1.0, "adopt")
    study = combine_score(1.0, 1.0, "study")
    assert adopt == 1.0 and study == 1.0
    lowq = combine_score(1.0, 0.0, "adopt")
    lowq_study = combine_score(1.0, 0.0, "study")
    assert lowq < lowq_study  # study tolerates low quality more
