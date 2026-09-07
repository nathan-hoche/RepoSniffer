# Security Policy

RepoSniffer is a developer tool that queries the public GitHub API and caches
results locally. Its main surface is:

- **The `reposniffer` Python package** (CLI + MCP server), run by users in their
  own environment with their own `GITHUB_TOKEN`.
- **The local SQLite cache** (`~/.cache/reposniffer/reposniffer.db`).

We treat security issues seriously and will respond promptly.

## Supported versions

Only the latest released version on PyPI is supported. We recommend always
running the current release.

## Reporting a vulnerability

**Do not open a public issue for a security vulnerability.**

Please report it privately through GitHub's private vulnerability reporting:

1. Go to https://github.com/nathan-hoche/RepoSniffer/security/advisories
2. Click **Report a vulnerability**
3. Describe the issue, its impact, and (if possible) a minimal reproduction.

If private vulnerability reporting is not available on the repository, open a
public issue titled `[SECURITY] ...` with as much detail as you're comfortable
sharing, or contact the maintainer directly on GitHub.

### What to include

- Which component is affected (CLI, MCP server, cache, engine).
- Steps to reproduce and the exact input used.
- The impact (e.g. token leakage, path traversal, denial of service) and your
  severity assessment if you have one.

## What we care about

Things we consider in scope:

- Exposure or misuse of the user's `GITHUB_TOKEN` or other secrets.
- Path traversal or unsafe file handling in the SQLite cache.
- Malicious input (e.g. a crafted README/description) causing code execution or
  excessive resource use.
- Supply-chain concerns in dependencies.

Out of scope (by design):

- Data the public GitHub API already exposes — RepoSniffer only re-presents
  public repository metadata and READMEs.
- Rate limiting from GitHub's API itself.

## Response timeline

- Acknowledgement within **48 hours**.
- Initial triage and severity assessment within **1 week**.
- We coordinate on a fix and will credit you in the advisory (unless you prefer
  to stay anonymous).

## Security of `GITHUB_TOKEN`

RepoSniffer never logs or transmits your token anywhere except to the GitHub
API. If you believe your token may have been exposed, revoke it at
https://github.com/settings/tokens immediately.