# Contributing to RepoSniffer

Thanks for wanting to contribute! RepoSniffer is a small, focused project, so the
contribution surface is intentionally small — but every addition matters.

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating you
agree to uphold it.

## Table of contents

- [Ways to contribute](#ways-to-contribute)
- [Development setup](#development-setup)
- [Project structure](#project-structure)
- [Coding standards](#coding-standards)
- [Tests](#tests)
- [The eval harness](#the-eval-harness)
- [Commit conventions](#commit-conventions)
- [Pull request workflow](#pull-request-workflow)
- [Release process](#release-process)

## Ways to contribute

1. **Report a bug** — open an issue with a minimal reproduction. Repos you searched,
   the exact query, and the `--json` output are gold.
2. **Suggest a feature** — open a feature-request issue first so we can discuss it
   before you write code.
3. **Fix a bug or add a feature** — see [Pull request workflow](#pull-request-workflow).
4. **Add eval cases** — the fastest way to improve ranking quality. One query + the
   known-good repo(s) in `eval/queries.py`. No code needed.
5. **Docs** — README, this file, docstrings, examples.

**Good first contributions**: an eval case, a typo/README fix, or any issue labeled
`good first issue`.

## Development setup

Requires [uv](https://docs.astral.sh/uv/) (Python 3.12+; we develop on 3.14).

```bash
uv sync                 # install dependencies (incl. dev)
uv run ruff check .     # lint
uv run ruff format .    # format
uv run pyright          # type check
uv run pytest           # tests (offline — no network, no token)
```

All four must be green before a PR is reviewable.

For manual testing against real GitHub data, set `GITHUB_TOKEN` (a fine-grained
token with `public_repo` read access is enough; higher rate limits than
unauthenticated):

```bash
export GITHUB_TOKEN=ghp_...
uv run reposniffer "markdown editor live preview" --top-k 5
```

## Project structure

```
src/reposniffer/
  config.py        # env-driven settings
  cache.py         # sqlite store (repos, readmes, embeddings, query cache)
  engine/
    github.py      # GitHub REST client + search query builder + text/snippet utils
    embed.py       # Embedder protocol: local fastembed + OpenAI-compatible API
    score.py       # quality + license-category + lexical scoring
    search.py      # orchestration (Engine)
  mcp/server.py    # MCPServer (mcp 2.x) — the agent-facing tools
  cli.py           # Typer CLI
eval/              # golden query -> repo eval harness
docs/              # demo.gif, icon.png
```

The engine is the core; `mcp` and `cli` are thin front-ends. Keep it that way —
new features belong in `engine/`, not in the CLIs.

## Coding standards

- **Python >= 3.12**, modern typing (`from __future__ import annotations`).
- **Formatting/lint**: ruff, line length 100. `uv run ruff format .` then
  `uv run ruff check .` before committing.
- **Types**: pyright clean. No `Any` leaks into public signatures.
- **No comments** unless they explain a *why* the code can't (docstrings on
  public functions and MCP tools are fine and encouraged — MCP tool docstrings
  become the agent-facing descriptions).
- **Keep dependencies minimal.** Before adding one, ask: does it pull torch /
  heavy native code? Would a stdlib approach work? The local embedding path is
  deliberately ONNX-based (`fastembed`) so Python 3.14 needs no torch wheels.
- **Pluggable by design**: embedder and GitHub client are injectable protocols;
  tests swap in fakes. Keep new integration points behind the same seams.
- **Cache versioning**: if you change what gets embedded or how candidates are
  fetched, bump `QUERY_CACHE_VERSION` / `EMBEDDING_CACHE_VERSION` so stale data
  can never poison results.

## Tests

Tests are **offline**: they use a fake GitHub transport and a fake embedder from
`tests/conftest.py`, never real network calls or API tokens.

- Add a test for every behavior change.
- For scoring/query-building changes, extend `tests/test_score.py` /
  `tests/test_upgrades.py`.
- For end-to-end search behavior, extend `tests/test_search.py` using the
  fixtures in `conftest.py`.

Run `uv run pytest` — it should stay green and fast.

## The eval harness

Ranking quality is the product. The eval measures it objectively:

- Add a golden case to `eval/queries.py`:

  ```python
  {
      "query": "websocket rate limiting",
      "expected": ["owner/repo", "other/valid-answer"],
      "intent": "adopt",  # or "study"
  }
  ```

  Only include repos that are genuinely good answers — the eval is a quality bar,
  not a checklist.

- Run it (needs a token; each query fetches ~50 READMEs):

  ```bash
  GITHUB_TOKEN=ghp_... uv run python -m eval.run
  ```

- A change that regresses `hit@3` / `hit@5` should be flagged in the PR. Known
  limitations are documented in the README's Eval section — don't silently grow
  the golden set to hide a regression.

## Commit conventions

Use [Conventional Commits](https://www.conventionalcommits.org/). The repo's
history follows this — match it:

- `feat:` — new user-facing behavior (engine, CLI, MCP tool)
- `fix:` — a bug fix (e.g. "fix: valid JSON output")
- `docs:` — README, CONTRIBUTING, examples
- `test:` — tests only
- `build:` / `ci:` — packaging / workflows
- `perf:` — performance

Format: `type(scope): short imperative summary`. Keep commits small and focused.

## Pull request workflow

1. **Open an issue first** for anything non-trivial (feature or non-obvious bug).
   Link the PR to it (`Closes #12`).
2. **Branch from `main`**, keep the PR small and single-purpose. Prefer several
   small PRs over one large one.
3. Implement, then verify locally:

   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run pyright
   uv run pytest
   ```

4. If you changed retrieval behavior, also run the eval and report the numbers in
   the PR body (see [the eval harness](#the-eval-harness)).
5. Push and open the PR with the template filled in.

**Review rules**

- CI must pass (lint, format, type, tests all run on every push/PR).
- One approving review required for merge (maintainer).
- No self-merges except for trivial maintainer changes.

## Release process

Maintainers only. Releases are tags; the `Publish to PyPI` workflow handles the
rest via trusted publishing:

```bash
# 1. bump the version in pyproject.toml AND src/reposniffer/__init__.py
# 2. commit: "build: bump version to X.Y.Z"
git tag vX.Y.Z
git push origin main vX.Y.Z
```

Semver: breaking behavior change → minor bump (0.x); fixes and additive tweaks →
patch bump.