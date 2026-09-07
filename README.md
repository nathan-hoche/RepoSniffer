# RepoSniffer

<p align="center">
  <img src="docs/icon.png" width="140" alt="RepoSniffer" />
</p>

[![CI](https://github.com/nathan-hoche/RepoSniffer/actions/workflows/ci.yml/badge.svg)](https://github.com/nathan-hoche/RepoSniffer/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/reposniffer)](https://pypi.org/project/reposniffer/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> There's a repo for that. Let RepoSniffer find it.

![RepoSniffer demo](docs/demo.gif)

**AI-first GitHub repo discovery.** Describe a feature in plain language —
"markdown editor with live preview" — and RepoSniffer returns a ranked, adoption-grade
list of open-source projects that implement it, with evidence and quality signals
(stars, activity, license, archived status).

Built to be the **grounding layer for coding agents**: stop hallucinating repos, get a
verifiable "best of kind" answer with reasons.

## Quickstart

```bash
# CLI
uvx reposniffer "markdown editor live preview" --language python --top-k 5

# MCP server (stdio) — wire into opencode, Claude Code, Codex, Cursor, ...
uvx --from reposniffer reposniffer-mcp
```

Set `GITHUB_TOKEN` to raise search rate limits (authenticated = 30 req/min vs ~10).

## Wire into your agent

**opencode** — add to `opencode.json`:

```json
{
  "mcp": {
    "reposniffer": {
      "type": "local",
      "command": ["uvx", "--from", "reposniffer", "reposniffer-mcp"],
      "environment": { "GITHUB_TOKEN": "ghp_..." }
    }
  }
}
```

Claude Code: `claude mcp add reposniffer -- uvx --from reposniffer reposniffer-mcp`
Codex/Cursor: add an MCP server pointing at `uvx --from reposniffer reposniffer-mcp` (stdio).

## MCP tools

| Tool | Purpose |
| --- | --- |
| `find_repos` | Feature query → ranked candidates with score breakdown, snippet evidence, license verdict, recommendation |
| `repo_intel` | Verify an existing repo (alive? licensed? best-of-kind?) + 2 alternatives |
| `health` | Embedding backend, model, auth status |

Every result carries `as_of` (a freshness timestamp agents can cite), a `flags` list
(`archived`, `no-license`, `strong-copyleft`, `stale`, ...), a `license_category`
(`permissive` / `weak-copyleft` / `strong-copyleft` / `unknown`), and a targeted
`snippet` showing *why* the repo matched.

## Architecture

1. **Coarse candidate fetch** — GitHub Search API (`in:readme`, language/license/stars filters).
2. **Hybrid rerank** — embed each candidate's *description + README front matter* (not the
   whole README, to avoid dilution), cosine vs embedded query, plus a lexical-overlap boost
   for literal matches.
3. **Quality scoring** — popularity (log stars), activity (pushed_at half-life), license
   category, archived penalty; weights differ by `intent` (`adopt` vs `study`).
4. **Adoption safety** — permissive/weak/strong-copyleft classification flags GPL/AGPL repos
   before you depend on them.
5. **Local SQLite cache** — repos, READMEs, embeddings, query results → fast repeat queries,
   index grows over time.

Embeddings are pluggable: default is a zero-config **local** `fastembed` ONNX model
(`BAAI/bge-base-en-v1.5`, no torch, no API key); set `REPOSNIFFER_EMBED_BACKEND=api` plus an OpenAI-compatible
endpoint for stronger quality.

## Eval

Ground-truth queries live in `eval/queries.py` (feature → known-good repos). Run with a
token (each query fetches ~50 READMEs):

```bash
GITHUB_TOKEN=ghp_... uv run python -m eval.run
```

Reports hit@1 / hit@3 / hit@5. Current live result: **hit@1 0.83, hit@3 0.83, hit@5 0.83**.

Known limitation: the candidate stage depends on GitHub Search API relevance, which can
fail to recall canonical repos with weak descriptions/READMEs (e.g. `Kozea/WeasyPrint`
— description is just "The awesome document factory"). Semantic rerank can only rank
what the candidate fetch surfaces.

## Project layout

```
src/reposniffer/
  config.py        # env-driven settings
  cache.py         # sqlite store (repos, readmes, embeddings, query cache)
  engine/
    github.py      # GitHub REST client + search query builder + text/snippet utils
    embed.py       # Embedder protocol: local fastembed + OpenAI-compatible API
    score.py       # quality + license-category + lexical scoring
    search.py      # orchestration (Engine)
  mcp/server.py    # MCPServer (mcp 2.x)
  cli.py           # Typer CLI
eval/              # golden query → repo eval harness
tests/             # offline (fake transport + fake embedder)
```

## Development

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

CI (lint/format/type/tests) runs on every push and PR. Publishing to PyPI happens on `v*`
tags via trusted publishing — enable it once on the PyPI project settings, then:
`git tag v0.1.0 && git push --tags`.

Note: mcp 2.x is used — `MCPServer` (FastMCP was renamed in mcp 2.0). Pin `mcp<2` if you need the v1 API.

## Contributing

We welcome contributions — bugs, features, docs, and eval cases. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) first; it covers the dev setup, coding
standards, tests, the eval harness, and the PR workflow.

- **Found a bug?** Open an issue with the exact query and output.
- **Have a feature idea?** Discuss it in an issue before writing code.
- **Reporting a vulnerability?** See [SECURITY.md](SECURITY.md) — don't post it publicly.
- This project follows a [Code of Conduct](CODE_OF_CONDUCT.md).

## License

MIT