---
title: Getting started
description: Install and run RepoSniffer.
---

## Requirements

- **Python 3.12+** and [uv](https://docs.astral.sh/uv/) (or `pip`).
- A **GitHub token** is strongly recommended. RepoSniffer reads `GITHUB_TOKEN`; if unset,
  it falls back to `gh auth token` automatically. Without a token you get GitHub's
  unauthenticated limit (60 requests/hour) — one query can exhaust it.

## Install

```bash
# Run without installing (recommended)
uvx reposniffer --help

# Or install into a virtual environment
uv tool install reposniffer
# or
pip install reposniffer
```

The first run downloads the embedding model once (~209 MB, cached in
`~/.cache/fastembed`). Set `REPOSNIFFER_EMBED_MODEL=BAAI/bge-small-en-v1.5` for a smaller
~90 MB footprint at slightly lower precision.

## First search

```bash
export GITHUB_TOKEN=ghp_...   # or rely on `gh auth token` fallback
reposniffer search "markdown editor with live preview" --top-k 5
```

```
RepoSniffer — 'markdown editor with live preview' (adopt)
┏━━━┳━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ # ┃ Repo         ┃ Stars ┃ Lang      ┃ License ┃ Activity ┃ Recommen…  ┃
┡━━━╇━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 1 │ marktext/…   │ 61134 │ TypeScript│ MIT      │ 1.00     │ strong cand │
```

## Verify a repo before adopting it

```bash
reposniffer intel ianstormtaylor/slate
# ianstormtaylor/slate — healthy and licensed
#   https://github.com/ianstormtaylor/slate | license MIT (permissive) · stars 31754
```

## JSON output

Every command supports `--json` for scripting and agents:

```bash
reposniffer search "websocket rate limiting" --json | jq '.results[0].full_name'
```

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `GITHUB_TOKEN` | — | GitHub API token (falls back to `gh auth token`) |
| `REPOSNIFFER_EMBED_BACKEND` | `local` | `local` (fastembed) or `api` (OpenAI-compatible) |
| `REPOSNIFFER_EMBED_MODEL` | `BAAI/bge-base-en-v1.5` | Local embedding model |
| `REPOSNIFFER_EMBED_API_BASE` | `https://api.openai.com/v1` | API embedder endpoint |
| `REPOSNIFFER_EMBED_API_KEY` | — | API embedder key |
| `REPOSNIFFER_DB` | `~/.cache/reposniffer/…` | SQLite cache path |