# Launch checklist — make RepoSniffer trendy

Copy-paste these for launch day. Update links after publishing.

## 1) Hacker News — Show HN

Title: Show HN: RepoSniffer – semantic GitHub repo discovery for coding agents (MCP + CLI)

Body:
```
RepoSniffer: describe a feature in plain language ("markdown editor with live preview") and get a ranked, adoption-grade list of open-source projects.

- Hybrid rerank: GitHub Search API → README embeddings (bge-base-en-v1.5 local ONNX) + lexical boost
- Quality signals: stars/activity/license (permissive/weak/strong-copyleft), archived/stale flags
- Evidence snippets + as_of timestamp agents can cite
- MCP server (find_repos, repo_intel, health) for opencode/Claude Code/Codex/Cursor + Typer CLI

Live eval hit@1 0.83 on golden queries. Local SQLite cache, pluggable OpenAI-compatible embeddings.

Try: uvx reposniffer "markdown editor live preview" --top-k 5

Repo: https://github.com/nathan-hoche/RepoSniffer
Docs: https://nathan-hoche.github.io/RepoSniffer/
PyPI: https://pypi.org/project/reposniffer/
```

## 2) Reddit r/Python, r/MachineLearning, r/mcp

Title: AI-first GitHub repo discovery — stop hallucinating repos, get verifiable best-of-kind answers

Body: same as HN + add opencode.json snippet from README.

## 3) X / Twitter

Thread:
1/ There's a repo for that. But agents keep hallucinating it.

RepoSniffer = semantic GitHub discovery for agents. Describe a feature → get ranked, adoption-grade repos with evidence.

2/ MCP server + CLI. GitHub Search → README embeddings (bge-base) + lexical rerank + quality/license scoring. hit@1 0.83.

3/ uvx reposniffer "markdown editor live preview" --top-k 5
MCP: uvx --from reposniffer reposniffer-mcp

GitHub: https://github.com/nathan-hoche/RepoSniffer
Docs: https://nathan-hoche.github.io/RepoSniffer/

## 4) MCP registries (do after v0.1.4 tag)

- https://github.com/modelcontextprotocol/registry — PR with server.json (already in repo)
- https://smithery.ai — `smithery.yaml` already in repo, run `npx @smithery/cli publish`
- https://glama.ai/mcp/servers, https://pulsemcp.com, https://mcp.so — submit URL https://github.com/nathan-hoche/RepoSniffer
- Update README MCP badge link once listed

## 5) GitHub repo settings (manual)

- Settings → Social preview → Upload docs/social-preview.png (1280x640)
- Verify Topics: agent, cli, embeddings, github-api, mcp, semantic-search (done)
- Enable Sponsors via .github/FUNDING.yml (added)

## 6) Product Hunt (optional week-2)

Tagline: AI-first GitHub repo discovery for coding agents
