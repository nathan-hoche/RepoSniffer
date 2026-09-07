from __future__ import annotations

import asyncio
from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import BaseModel, Field

from reposniffer.config import Settings
from reposniffer.engine.search import build_engine


class FindReposParams(BaseModel):
    query: str = Field(
        description="Plain-language description of the feature, pattern, or narrow library you want."
    )
    intent: str = Field(
        default="adopt",
        description="adopt = pick a dependency to use; study = reference implementation to learn from.",
    )
    language: str | None = Field(
        default=None, description="Optional language filter, e.g. 'python', 'rust'."
    )
    license: str | None = Field(
        default=None, description="Optional SPDX license key, e.g. 'mit', 'apache-2.0'."
    )
    min_stars: int | None = Field(default=None, description="Optional minimum stars filter.")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of ranked repos to return.")
    include_archived: bool = Field(
        default=False, description="Include archived repos (usually avoid)."
    )


class RepoIntelParams(BaseModel):
    owner_repo: str = Field(description="The 'owner/repo' you are considering, e.g. 'encode/uv'.")
    query: str | None = Field(
        default=None, description="Optional feature query to frame the comparison."
    )
    top_k: int = Field(default=2, ge=0, le=5, description="How many alternative repos to suggest.")


class HealthParams(BaseModel):
    pass


mcp = MCPServer("reposniffer")


def _engine() -> Any:
    return build_engine(Settings())


@mcp.tool()
def find_repos(params: FindReposParams) -> dict[str, Any]:
    """Rank open-source GitHub projects that implement a described feature.

    Use when an agent needs to pick a library/project to adopt or study, and
    wants a verifiable, adoption-grade verdict with evidence and quality signals
    (stars, activity, license, archived status) instead of a hallucinated guess.
    """
    if params.intent not in {"adopt", "study"}:
        raise ValueError("intent must be 'adopt' or 'study'")
    results = _engine().search(
        query=params.query,
        language=params.language,
        license_key=params.license,
        min_stars=params.min_stars,
        intent=params.intent,  # type: ignore[arg-type]
        top_k=params.top_k,
        include_archived=params.include_archived,
    )
    return {
        "query": params.query,
        "intent": params.intent,
        "embedding_model": _engine().model_name,
        "results": results,
    }


@mcp.tool()
def repo_intel(params: RepoIntelParams) -> dict[str, Any]:
    """Verify an existing repo the agent already found: is it alive, licensed,
    and best-of-kind? Returns a status verdict plus a few alternatives.

    Use BEFORE committing to a dependency to catch archived/stale/no-license repos.
    """
    return _engine().repo_intel(
        owner_repo=params.owner_repo, query=params.query, top_k=params.top_k
    )


@mcp.tool()
def health() -> dict[str, Any]:
    """Report embedding backend, model, and GitHub auth status."""
    return Settings().summary()


def main() -> None:
    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
