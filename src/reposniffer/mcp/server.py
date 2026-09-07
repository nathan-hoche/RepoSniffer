from __future__ import annotations

import asyncio
import threading
import traceback
from typing import Any

from mcp.server.mcpserver import MCPServer

from reposniffer.config import Settings
from reposniffer.engine.search import build_engine

mcp = MCPServer("reposniffer")

_engine_singleton: Any | None = None
_engine_lock = threading.Lock()


def _engine() -> Any:
    global _engine_singleton
    if _engine_singleton is None:
        with _engine_lock:
            if _engine_singleton is None:
                _engine_singleton = build_engine(Settings())
    return _engine_singleton


@mcp.tool()
def find_repos(
    query: str,
    intent: str = "adopt",
    language: str | None = None,
    license: str | None = None,
    min_stars: int | None = None,
    top_k: int = 5,
    include_archived: bool = False,
) -> dict[str, Any]:
    """Rank open-source GitHub projects that implement a described feature.

    Use when an agent needs to pick a library/project to adopt or study, and
    wants a verifiable, adoption-grade verdict with evidence and quality signals
    (stars, activity, license, archived status) instead of a hallucinated guess.
    """
    if intent not in {"adopt", "study"}:
        raise ValueError("intent must be 'adopt' or 'study'")
    if not (1 <= top_k <= 20):
        raise ValueError("top_k must be between 1 and 20")
    try:
        engine = _engine()
        results = engine.search(
            query=query,
            language=language,
            license_key=license,
            min_stars=min_stars,
            intent=intent,  # type: ignore[arg-type]
            top_k=top_k,
            include_archived=include_archived,
        )
    except Exception as exc:
        traceback.print_exc()
        return {"error": f"{type(exc).__name__}: {exc}"}
    return {
        "query": query,
        "intent": intent,
        "as_of": results[0]["as_of"] if results else None,
        "embedding_model": engine.model_name,
        "results": results,
    }


@mcp.tool()
def repo_intel(
    owner_repo: str,
    query: str | None = None,
    top_k: int = 2,
) -> dict[str, Any]:
    """Verify an existing repo the agent already found: is it alive, licensed,
    and best-of-kind? Returns a status verdict plus a few alternatives.

    Use BEFORE committing to a dependency to catch archived/stale/no-license repos.
    """
    try:
        return _engine().repo_intel(owner_repo=owner_repo, query=query, top_k=top_k)
    except Exception as exc:
        traceback.print_exc()
        return {"error": f"{type(exc).__name__}: {exc}"}


@mcp.tool()
def health() -> dict[str, Any]:
    """Report embedding backend, model, and GitHub auth status."""
    return Settings().summary()


def main() -> None:
    threading.Thread(target=_engine, daemon=True).start()  # warm up in the background
    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
