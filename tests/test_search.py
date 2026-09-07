from __future__ import annotations

from reposniffer.cache import Store
from reposniffer.engine.search import Engine


def test_search_returns_ranked_results(engine: Engine):
    results = engine.search("markdown editor with live preview", intent="adopt", top_k=5)
    assert len(results) == 3
    assert results[0]["full_name"] == "testcorp/markdown-live"
    assert results[0]["rank"] == 1
    assert results[0]["license"] == "MIT"
    assert results[0]["license_category"] == "permissive"
    assert results[0]["recommendation"] == "strong candidate"
    assert results[0]["snippet"]
    assert results[0]["as_of"]
    assert results[0]["has_readme"] is True


def test_search_prefers_healthy_over_archived(engine: Engine):
    results = engine.search("websocket rate limiting", intent="adopt", top_k=5)
    names = [r["full_name"] for r in results]
    assert names.index("testcorp/websocket-throttle") < names.index("dead/old-project")


def test_search_flags_archived_and_no_license(engine: Engine):
    results = engine.search("websocket rate limiting", intent="adopt", top_k=5)
    dead = next(r for r in results if r["full_name"] == "dead/old-project")
    assert "archived" in dead["flags"]
    assert "stale" in dead["flags"]


def test_search_lexical_boost(engine: Engine):
    results = engine.search("websocket rate limiting", intent="adopt", top_k=5)
    top = results[0]
    assert top["full_name"] == "testcorp/websocket-throttle"
    assert top["lexical"] > 0


def test_search_caches_embeddings(engine: Engine, store: Store):
    engine.search("markdown editor", top_k=5)
    stats = store.stats()
    assert stats["embeddings"] == 3


def test_repo_intel_flags_archived(engine: Engine):
    result = engine.repo_intel("dead/old-project")
    assert "archived" in result["status"]


def test_repo_intel_healthy(engine: Engine):
    result = engine.repo_intel("testcorp/markdown-live")
    assert result["status"] == "healthy and licensed"
    assert result["alternatives"]
    assert result["license_category"] == "permissive"
    assert result["as_of"]
