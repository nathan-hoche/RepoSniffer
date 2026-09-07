# RepoSniffer

> There's a repo for that. Let RepoSniffer find it.

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
uvx reposniffer-mcp
```

Set `GITHUB_TOKEN` to raise search rate limits (authenticated = 30 req/min vs ~10).

## Wire into your agent

**opencode** — add to `opencode.json`:

```json
{
  "mcp": {
    "reposniffer": {
      "type": "local",
      "command": ["uvx", "reposniffer-mcp"],
      "environment": { "GITHUB_TOKEN": "ghp_..." }
    }
  }
}
```

Claude Code: `claude mcp add reposniffer -- uvx reposniffer-mcp`
Codex/Cursor: add an MCP server pointing at `uvx reposniffer-mcp` (stdio).

## MCP tools

| Tool | Purpose |
| --- | --- |
| `find_repos` | Feature query → ranked candidates with score breakdown, evidence, recommendation |
| `repo_intel` | Verify an existing repo (alive? licensed? best-of-kind?) + 2 alternatives |
| `health` | Embedding backend, model, auth status |

## Architecture

1. **Coarse candidate fetch** — GitHub Search API (`in:readme`, language/license/stars filters).
2. **Semantic rerank** — embed each candidate README, cosine vs embedded query.
3. **Quality scoring** — popularity (log stars), activity (pushed_at half-life), license,
   archived penalty; weights differ by `intent` (`adopt` vs `study`).
4. **Local SQLite cache** — repos, READMEs, embeddings, query results → fast repeat queries,
   index grows over time.

Embeddings are pluggable: default is a zero-config **local** `fastembed` ONNX model
(no torch, no API key); set `REPOSNIFFER_EMBED_BACKEND=api` plus an OpenAI-compatible
endpoint for stronger quality.

## Project layout

```
src/reposniffer/
  config.py        # env-driven settings
  cache.py         # sqlite store (repos, readmes, embeddings, query cache)
  engine/
    github.py      # GitHub REST client + search query builder
    embed.py       # Embedder protocol: local fastembed + OpenAI-compatible API
    score.py       # quality + semantic scoring
    search.py      # orchestration (Engine)
  mcp/server.py    # FastMCP server
  cli.py           # Typer CLI
eval/              # golden query → repo eval harness
tests/             # offline (fake transport + fake embedder)
```

## Development

```bash
uv sync
uv run ruff check .
uv run pyright
uv run pytest
```

Note: mcp 2.x is used — `MCPServer` (FastMCP was renamed in mcp 2.0). Pin `mcp<2` if you need the v1 API.

## License

MIT