---
title: Architecture
description: How RepoSniffer works under the hood.
---

RepoSniffer is a two-tier semantic search over GitHub. The candidate stage solves
*recall*; the rerank stage solves *precision*.

## Pipeline

```
query ──▶ embed (query vector)
              │
              ▼
   GitHub Search API ──▶ candidate repos ──▶ fetch READMEs
   (key terms + filters)        │                │
                                ▼                ▼
                    quality scoring ◀── embed description + README front matter
                                │                │
                                ▼                ▼
                    combine (relevance × quality) ──▶ ranked results + evidence
```

### 1. Candidate fetch (GitHub Search API)

GitHub's literal keyword search doesn't handle natural language well, so the query is
prepared carefully:

- **Stopwords stripped** — "ASGI web framework with automatic API documentation"
  becomes `ASGI web framework API documentation in:readme` (verbose sentences kill
  recall).
- **Topic-assisted variant** — a second query adds `topic:` qualifiers for common
  topical words (e.g. `pdf html topic:pdf topic:html`), unioned with the primary.
- **Curated-list filtering** — awesome/awesome-list repos are removed from candidates
  (they can be 50%+ of raw results and are rarely what you want to depend on).

### 2. Rerank (semantic)

Each candidate's **description + README front matter** is embedded (not the whole
README — badges and contribution sections dilute the signal). Relevance is a hybrid:

```
relevance = 0.8 × cosine(query, readme)  +  0.2 × lexical overlap
```

The lexical term rewards literal keyword matches; the cosine term captures intent.

### 3. Quality scoring

Every repo gets an adoption-grade quality score:

```
quality = 0.4 × activity + 0.2 × license + 0.4 × popularity
```

- **activity** — exponential decay of `pushed_at` (half-life ~6 months)
- **license** — SPDX present / absent
- **popularity** — log-scaled stars + forks
- **archived** repos get a hard penalty (× 0.25)

License is further classified as `permissive` / `weak-copyleft` / `strong-copyleft` /
`unknown`, so GPL/AGPL repos are flagged before you depend on them.

The final score weights `relevance` vs `quality` by intent: `adopt` favors quality
(50/50), `study` favors relevance (75/25).

## Embeddings

Embeddings are **pluggable** behind a small protocol. The default is a local
`fastembed` ONNX model (`BAAI/bge-base-en-v1.5`, ~209 MB, no torch), so it works on
Python 3.14 with zero API keys. Setting `REPOSNIFFER_EMBED_BACKEND=api` switches to
any OpenAI-compatible embeddings endpoint.

## Cache

A SQLite store (`~/.cache/reposniffer/reposniffer.db`) caches repos, READMEs,
embeddings, and query results with TTLs. Repeat queries skip GitHub entirely.
Schema changes bump `QUERY_CACHE_VERSION` / `EMBEDDING_CACHE_VERSION` so stale data
can never poison results.

## Code layout

```
src/reposniffer/
  config.py        # env-driven settings
  cache.py         # sqlite store
  engine/
    github.py      # GitHub client + query building + text/snippet utils
    embed.py       # Embedder protocol (fastembed + API)
    score.py       # quality + license + lexical scoring
    search.py      # Engine orchestration (build_engine)
  mcp/server.py    # MCPServer (mcp 2.x)
  cli.py           # Typer CLI
```