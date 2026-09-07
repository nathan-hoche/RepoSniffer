---
title: CLI reference
description: The reposniffer command-line interface.
---

## `reposniffer search`

Find open-source projects that implement a described feature.

```bash
reposniffer search QUERY [options]
```

| Option | Description |
| --- | --- |
| `--intent, -i` | `adopt` (pick a dependency) or `study` (reference to learn from). Default `adopt`. |
| `--language, -l` | Filter by language, e.g. `python`, `rust`. |
| `--license` | Filter by SPDX license key, e.g. `mit`, `apache-2.0`. |
| `--min-stars` | Minimum stars. |
| `--top-k` | Number of results (1–20). Default 5. |
| `--json` | Emit JSON instead of a table. |

```bash
reposniffer search "markdown editor live preview" --language python --top-k 3
```

## `reposniffer intel`

Verify a specific repo you already found: is it alive, licensed, and best-of-kind?

```bash
reposniffer intel OWNER/REPO [options]
```

| Option | Description |
| --- | --- |
| `--query, -q` | Optional feature query to frame the comparison. |
| `--top-k` | How many alternative repos to suggest (0–5). Default 2. |
| `--json` | Emit JSON. |

```bash
reposniffer intel ianstormtaylor/slate
```

## `reposniffer doctor`

Report embedding backend, model, and GitHub auth status — useful for diagnosing
rate-limit or model issues.

```bash
reposniffer doctor
```

## Exit codes

- `0` — success
- `1` — error (including GitHub API/rate-limit failures, reported with a hint)