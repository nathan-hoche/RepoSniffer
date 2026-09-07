# Changelog

All notable changes to RepoSniffer are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-09-07

### Added
- `server.json` (MCP registry) + `smithery.yaml` (Smithery) manifests; `site/public/og.png` OG image + Starlight `head` tags for link unfurls.
- `docs/LAUNCH.md` launch playbook (HN/Reddit/X/mcp registries), `docs/social-preview.png` as site OG image.
- `.github/FUNDING.yml` (GitHub Sponsors), PyPI `[project.urls]` (Homepage/Docs/Repo/Issues/Changelog), `Downloads` badge and `MCP` badge + star-history chart + "Why not just GitHub Search?" comparison in README.
- `Development Status :: 3 - Alpha` → `4 - Beta`.

### Fixed
- Thread-safe `Store` (`check_same_thread=False` + `RLock`) for MCP background warm-up + threadpool callers; offline `scripts/check_mcp.py` + `mcp.yml` CI.

## [0.1.3] - 2026-09-07

### Added
- `GITHUB_TOKEN` now falls back to `gh auth token` when the env var is unset,
  so the tool works out of the box for users with the GitHub CLI authenticated
  (no more accidental unauthenticated rate-limit exhaustion).

### Fixed
- MCP server warms up the engine in a background thread at startup, so the
  first tool call doesn't pay model-load latency (which could exceed client
  MCP call timeouts). Thread-safe singleton.

## [0.1.2] - 2026-09-07

### Fixed
- MCP tools not exposed as callable in opencode: refactored from a single nested
  `params` object to flat, typed scalar arguments so clients surface them as
  callable tools.

### Changed
- Default embedding model `BAAI/bge-small-en-v1.5` → `BAAI/bge-base-en-v1.5`
  (384 → 768 dim). Eval hit@1 0.50 → 0.83; hit@3/hit@5 hold at 0.83.
- `EMBEDDING_CACHE_VERSION` bumped to invalidate stale embeddings.
- CLI `search --json` envelope now includes a top-level `as_of` timestamp.

## [0.1.1] - 2026-09-07

### Fixed
- `--json` output was corrupted by rich's line-wrapping inserting raw newlines
  inside strings; now written via `sys.stdout`.

### Changed
- Candidate-stage retrieval: stopword-stripped GitHub queries, curated/awesome-list
  filtering (up to 27/50 candidates were lists), 50 candidates, topic-assisted
  query variant (`topic:pdf topic:html`).
- Cache schema versioning so stale candidate/embedding data never poisons results.
- Live eval improved: hit@1 0.33→0.50, hit@3 0.50→0.83, hit@5 0.83.

### Added
- `GITHUB_TOKEN` onboarding warning on first CLI run.
- `docs/demo.gif` and `docs/icon.png`; README header updated.

## [0.1.0] - 2026-09-07

### Added
- Initial release: two-tier semantic search (GitHub Search API → README embeddings).
- MCP server (`find_repos`, `repo_intel`, `health`) via mcp 2.x `MCPServer`.
- Typer CLI (`search`, `intel`, `doctor`).
- Pluggable embeddings: local `fastembed` (ONNX, no torch) default; OpenAI-compatible API option.
- Hybrid relevance (cosine + lexical overlap), adoption-grade quality scoring,
  SPDX license classification (permissive/weak/strong-copyleft).
- Local SQLite cache (repos, READMEs, embeddings, query cache).
- Offline test suite; eval harness with hit@1/3/5.
- CI (lint/format/type/test) + trusted-publishing PyPI publish on `v*` tags.

[Unreleased]: https://github.com/nathan-hoche/RepoSniffer/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/nathan-hoche/RepoSniffer/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/nathan-hoche/RepoSniffer/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/nathan-hoche/RepoSniffer/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/nathan-hoche/RepoSniffer/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/nathan-hoche/RepoSniffer/releases/tag/v0.1.0