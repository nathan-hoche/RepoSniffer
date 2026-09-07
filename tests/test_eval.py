from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from eval import queries as eval_queries  # noqa: E402
from eval import run as eval_run  # noqa: E402


def test_eval_runner_reports_hit_rates(monkeypatch):
    def fake_results(query, intent, top_k):
        for case in eval_queries.GOLDEN[:2]:
            if case["query"] == query:
                expected = case["expected"][0]
                break
        else:
            expected = "unknown/repo"
        return [
            {
                "full_name": expected,
                "rank": 1,
                "recommendation": "strong candidate",
            }
        ]

    fake_engine = Mock()
    fake_engine.search.side_effect = fake_results
    fake_engine.close = Mock()
    monkeypatch.setattr(eval_run, "build_engine", lambda settings: fake_engine)
    monkeypatch.setattr(eval_run, "GOLDEN", eval_queries.GOLDEN[:2])

    report = eval_run.run(top_k=5)
    assert report["total"] == 2
    assert report["hit@1"] == 1.0
    assert report["hit@5"] == 1.0
    assert all(c["hit_at_any_k"] for c in report["cases"])
