---
title: Evaluation
description: How retrieval quality is measured.
---

Ranking quality is the product, so it's measured objectively rather than by vibes.

## The golden set

`eval/queries.py` holds feature queries mapped to known-good repos — the three
supported question types:

- a feature ("markdown editor with live preview")
- a tech pattern ("websocket rate limiting")
- a narrow library ("PDF generation from HTML")

Only genuinely good answers are included — the eval is a quality bar, not a checklist.

## Running it

Each query fetches ~50 READMEs, so it needs a token:

```bash
GITHUB_TOKEN=ghp_... uv run python -m eval.run
```

## Current results

| Metric | Value |
| --- | --- |
| hit@1 | 0.83 |
| hit@3 | 0.83 |
| hit@5 | 0.83 |

## Contributing a case

Add to `eval/queries.py`:

```python
{
    "query": "websocket rate limiting",
    "expected": ["owner/repo", "other/valid-answer"],
    "intent": "adopt",  # or "study"
}
```

Then run the eval to confirm it passes. A change that regresses `hit@3` / `hit@5`
should be flagged in the PR that caused it.

## Known limitations

The candidate stage depends on GitHub Search API relevance, which can fail to recall
canonical repos with weak descriptions or READMEs (e.g. `Kozea/WeasyPrint` — its
description is literally "The awesome document factory"). Semantic rerank can only
rank what the candidate fetch surfaces. If you hit this, the fix is usually a better
query variant or a topic qualifier, not a rerank tweak.