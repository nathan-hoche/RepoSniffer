# Changelog

All notable changes to RepoSniffer are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Community scaffolding: CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, issue/PR templates.
- Dependabot for pip + GitHub Actions dependencies.
- GitHub Releases from tags.

### Changed
- Default embedding model `BAAI/bge-small-en-v1.5` → `BAAI/bge-base-en-v1.5`
  (384 → 768 dim). Eval hit@1 0.50 → 0.83; hit@3/hit@5 hold at 0.83.
- `EMBEDDING_CACHE_VERSION` bumped to invalidate stale embeddings.

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

[Unreleased]: https://github.com/nathan-hoche/RepoSniffer/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/nathan-hoche/RepoSniffer/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/nathan-hoche/RepoSniffer/releases/tag/v0.1.0