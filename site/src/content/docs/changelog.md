---
title: Changelog
description: Release history.
---

The full changelog lives in [CHANGELOG.md](https://github.com/nathan-hoche/RepoSniffer/blob/main/CHANGELOG.md)
in the repository.

## 0.1.2

- **Fixed:** MCP tools now expose flat scalar parameters, making them discoverable
  as callable tools in opencode.
- **Changed:** default embedding model `bge-small` → `bge-base` (hit@1 0.50 → 0.83).

## 0.1.1

- **Fixed:** `--json` output corrupted by terminal line-wrapping.
- **Changed:** candidate-stage retrieval fixes (stopword queries, curated-list
  filtering, topic-assisted search, 50 candidates). Eval hit@1 0.33 → 0.50.

## 0.1.0

- Initial release: two-tier semantic search, MCP server, CLI, license classification,
  SQLite cache, eval harness, CI + PyPI publish.