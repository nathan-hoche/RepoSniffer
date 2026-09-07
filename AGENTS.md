# AGENTS.md

Guidance for AI agents (opencode, Claude Code, Codex, ...) working in this
repository. Human contributors should read [CONTRIBUTING.md](CONTRIBUTING.md).

## What this is

RepoSniffer is a semantic GitHub repo-discovery tool. Users describe a feature
("markdown editor with live preview") and get a ranked, adoption-grade list of
open-source projects, with quality signals and license verdicts. It ships as an
MCP server (primary) and a Typer CLI.

## Commands

```bash
uv sync                  # install deps (incl. dev); requires uv
uv run ruff check .      # lint
uv run ruff format .     # format (also: ruff format --check .)
uv run pyright           # type check — must be 0 errors
uv run pytest            # tests — all offline, no token/network needed
```

All four must pass before a change is done. There is no separate typecheck step
in the test suite; CI runs all four.

## Architecture

```
src/reposniffer/
  config.py        # env-driven settings (Settings dataclass)
  cache.py         # sqlite store: repos, readmes, embeddings, query cache
  engine/          # THE core. github.py, embed.py, score.py, search.py
    search.py      # Engine orchestration (build_engine factory)
  mcp/server.py    # MCPServer (mcp 2.x) — thin wrapper over Engine
  cli.py           # Typer — thin wrapper over Engine
eval/              # golden query -> repo eval harness (hit@1/3/5)
tests/             # offline tests (fake transport + fake embedder)
```

New features belong in `engine/`, never in the CLI/MCP front-ends.

## Rules of thumb

- **mcp 2.x**: `from mcp.server.mcpserver import MCPServer`. `FastMCP` was
  renamed in mcp 2.0 — do not import `mcp.server.fastmcp`.
- **No comments** unless they explain a non-obvious *why*. Docstrings on public
  functions and MCP tools are encouraged (MCP tool docstrings become the
  agent-facing tool descriptions).
- **Python >= 3.12**; add `from __future__ import annotations` at the top of
  every module.
- **Minimal dependencies**: prefer stdlib; avoid torch-family packages
  (embedding path is ONNX via `fastembed`).
- **Cache versioning**: if you change what gets embedded or how candidates are
  fetched, bump `QUERY_CACHE_VERSION` (engine/github.py) and/or
  `EMBEDDING_CACHE_VERSION` (engine/search.py) so stale data can't poison
  results.
- **Tests offline**: use the fakes in `tests/conftest.py`; never hit the real
  GitHub API or require a token in tests.

## Verification for retrieval changes

If you touch `engine/` (query building, embedding, scoring, candidates), run the
eval and report hit@1/3/5 before/after in the PR:

```bash
GITHUB_TOKEN=ghp_... uv run python -m eval.run   # needs a token, ~50 readmes/query
```

Never silently widen `eval/queries.py` to hide a regression — the golden set is
a quality bar.

## Commits

Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `build:`, `ci:`).
Match the existing history. Small, focused commits.