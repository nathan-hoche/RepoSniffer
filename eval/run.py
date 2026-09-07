from __future__ import annotations

from reposniffer.eval.queries import GOLDEN

from reposniffer.config import Settings
from reposniffer.engine.search import build_engine


def run(top_k: int = 5) -> dict:
    engine = build_engine(Settings())
    results_summary = []
    hits = 0
    for case in GOLDEN:
        results = engine.search(case["query"], intent=case["intent"], top_k=top_k)
        ranked = [r["full_name"] for r in results]
        hit = any(expected in ranked for expected in case["expected"])
        hits += int(hit)
        results_summary.append(
            {
                "query": case["query"],
                "hit": hit,
                "top": ranked,
                "expected": case["expected"],
            }
        )
    engine.close()
    return {
        "total": len(GOLDEN),
        "hits": hits,
        "hit_rate": round(hits / len(GOLDEN), 3) if GOLDEN else 0.0,
        "top_k": top_k,
        "cases": results_summary,
    }


def main() -> None:
    import json

    print(json.dumps(run(), indent=2))


if __name__ == "__main__":
    main()
