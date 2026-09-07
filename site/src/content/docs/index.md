---
title: RepoSniffer
description: Semantic GitHub repo discovery for coding agents — describe a feature, get the best open-source project.
hero:
  tagline: There's a repo for that. Let RepoSniffer find it.
  actions:
    - text: Get started
      link: /getting-started/
      icon: right-arrow
    - text: GitHub
      link: https://github.com/nathan-hoche/RepoSniffer
      icon: external
---

Semantic GitHub repo discovery for **coding agents** and humans. Describe a feature in
plain language — *"markdown editor with live preview"* — and RepoSniffer returns a ranked,
adoption-grade list of open-source projects that implement it, with evidence and quality
signals (stars, activity, license, archived status).

Built to be the **grounding layer for coding agents**: stop hallucinating repos, get a
verifiable "best of kind" answer with reasons.

:::tip[Agents]
RepoSniffer ships as an **MCP server** (`find_repos`, `repo_intel`, `health`) that plugs
into opencode, Claude Code, Codex and Cursor. See [Using with agents](/agents/).
:::

## Features

- **Semantic, not literal.** GitHub search + grep.app match keywords; RepoSniffer matches
  *intent* via README embeddings.
- **Adoption-grade verdicts.** Every result carries license classification, activity
  freshness, archived flags, and a recommendation — "good reusable project" beats
  "abandoned one".
- **Zero-config embedding.** Local ONNX model (`bge-base-en-v1.5`), no torch, no API key.
- **Pluggable.** Swap the local model for any OpenAI-compatible embeddings API.
- **Fast repeats.** Local SQLite cache of repos, READMEs, embeddings and query results.

## Quickstart

```bash
# CLI
uvx reposniffer "markdown editor live preview" --top-k 5

# MCP server (stdio) — wire into opencode, Claude Code, Codex, Cursor, ...
uvx --from reposniffer reposniffer-mcp
```

Set `GITHUB_TOKEN` (or have the GitHub CLI authenticated) to raise search rate limits.

## Quality

Retrieval quality is measured objectively against a golden eval set — currently
**hit@1 0.83, hit@3 0.83, hit@5 0.83**. See [Evaluation](/eval/).