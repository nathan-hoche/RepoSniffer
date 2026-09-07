from __future__ import annotations

from eval.queries import GOLDEN
from reposniffer.config import Settings
from reposniffer.engine.search import build_engine


def run(top_k: int = 5) -> dict:
    engine = build_engine(Settings())
    max_k = max(top_k, 5)
    hits = {k: 0 for k in (1, 3, 5)}
    cases: list[dict] = []
    for case in GOLDEN:
        results = engine.search(case["query"], intent=case["intent"], top_k=max_k)
        ranked = [r["full_name"] for r in results]
        expected = case["expected"]
        for k in hits:
            if any(e in ranked[:k] for e in expected):
                hits[k] += 1
        cases.append(
            {
                "query": case["query"],
                "expected": expected,
                "top": ranked,
                "hit_at_any_k": any(e in ranked for e in expected),
            }
        )
    engine.close()
    total = len(GOLDEN)
    return {
        "total": total,
        "hit@1": round(hits[1] / total, 3) if total else 0.0,
        "hit@3": round(hits[3] / total, 3) if total else 0.0,
        "hit@5": round(hits[5] / total, 3) if total else 0.0,
        "top_k": top_k,
        "cases": cases,
    }


def main() -> None:
    import json

    print(json.dumps(run(), indent=2))


if __name__ == "__main__":
    main()
