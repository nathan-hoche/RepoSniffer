---
title: Contributing
description: How to contribute to RepoSniffer.
---

We welcome contributions — bugs, features, docs, and eval cases.

**Please read the full [CONTRIBUTING.md](https://github.com/nathan-hoche/RepoSniffer/blob/main/CONTRIBUTING.md)** before opening a pull request. It covers the dev setup, coding standards, tests, the eval harness, and the review process.

## In short

- **Setup:** `uv sync`, then `uv run ruff check .`, `uv run ruff format --check .`,
  `uv run pyright`, `uv run pytest` must all pass.
- **Rules:** Python 3.12+, no comments unless they explain a *why*, minimal deps,
  features go in `engine/`, and bump cache versions if candidate/embedding logic changes.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) —
  `feat:`, `fix:`, `docs:`, `test:`, `build:`, `ci:`.
- **PRs:** small and focused, linked to an issue, with a filled template.
- **Retrieval changes:** report eval hit@1/3/5 before/after in the PR.

## Good first contributions

- Add an [eval case](/eval/) (query + known-good repo) — no code needed.
- Improve the docs or README.
- Any issue labeled `good first issue`.

This project follows the [Contributor Covenant](https://github.com/nathan-hoche/RepoSniffer/blob/main/CODE_OF_CONDUCT.md).
Report security issues privately via [SECURITY.md](https://github.com/nathan-hoche/RepoSniffer/blob/main/SECURITY.md).