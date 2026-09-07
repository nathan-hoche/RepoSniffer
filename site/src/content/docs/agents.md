---
title: Using with agents
description: Wire RepoSniffer into opencode, Claude Code, Codex and Cursor as an MCP server.
---

RepoSniffer is primarily an **MCP server** for coding agents. It gives agents a
hallucination-free way to find and verify open-source projects before adopting them.

## What the agent gets

| Tool | Purpose |
| --- | --- |
| `find_repos` | Feature query → ranked candidates with score breakdown, snippet evidence, license verdict, recommendation |
| `repo_intel` | Verify an existing repo (alive? licensed? best-of-kind?) + 2 alternatives |
| `health` | Embedding backend, model, GitHub auth status |

Every result carries an `as_of` freshness timestamp, a `flags` list
(`archived`, `no-license`, `strong-copyleft`, `stale`, …), a `license_category`
(`permissive` / `weak-copyleft` / `strong-copyleft` / `unknown`) and a targeted
`snippet` showing *why* the repo matched.

## Installation

```bash
uvx --from reposniffer reposniffer-mcp
```

The server speaks MCP over stdio. The first tool call warms up the embedding model
in the background.

## opencode

Add to your `opencode.json`:

```json
{
  "mcp": {
    "reposniffer": {
      "type": "local",
      "command": ["uvx", "--from", "reposniffer", "reposniffer-mcp"],
      "enabled": true,
      "environment": { "GITHUB_TOKEN": "ghp_..." }
    }
  }
}
```

If the first call times out, raise the MCP timeout:

```json
{ "experimental": { "mcp_timeout": 120000 } }
```

Restart opencode after adding the server.

## Claude Code

```bash
claude mcp add reposniffer -- uvx --from reposniffer reposniffer-mcp
```

## Codex and Cursor

Add an MCP server pointing at `uvx --from reposniffer reposniffer-mcp` (stdio) in the
respective MCP configuration UI.

## Agent workflow example

1. The agent needs a library for a task it hasn't built before.
2. It calls `find_repos(query="websocket rate limiting", intent="adopt")`.
3. It reads the top result's evidence snippet and recommendation.
4. Before committing, it calls `repo_intel(owner_repo="laurentS/slowapi")` to confirm
   the repo is alive, licensed, and best-of-kind — instead of hallucinating.
5. It cites the `as_of` timestamp in its answer.