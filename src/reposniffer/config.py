from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    github_token: str | None = field(default_factory=lambda: _env("GITHUB_TOKEN"))
    github_api_base: str = field(
        default_factory=lambda: (
            _env("GITHUB_API_BASE", "https://api.github.com") or "https://api.github.com"
        )
    )
    embed_backend: str = field(
        default_factory=lambda: _env("REPOSNIFFER_EMBED_BACKEND", "local") or "local"
    )
    embed_model: str = field(
        default_factory=lambda: (
            _env("REPOSNIFFER_EMBED_MODEL", "BAAI/bge-small-en-v1.5") or "BAAI/bge-small-en-v1.5"
        )
    )
    embed_api_base: str = field(
        default_factory=lambda: (
            _env("REPOSNIFFER_EMBED_API_BASE", "https://api.openai.com/v1")
            or "https://api.openai.com/v1"
        )
    )
    embed_api_key: str | None = field(default_factory=lambda: _env("REPOSNIFFER_EMBED_API_KEY"))
    embed_api_model: str = field(
        default_factory=lambda: (
            _env("REPOSNIFFER_EMBED_API_MODEL", "text-embedding-3-small")
            or "text-embedding-3-small"
        )
    )
    embed_dimension: int = field(
        default_factory=lambda: int(_env("REPOSNIFFER_EMBED_DIMENSION", "384") or "384")
    )
    request_timeout: float = field(
        default_factory=lambda: float(_env("REPOSNIFFER_TIMEOUT", "20") or "20")
    )
    search_per_page: int = field(
        default_factory=lambda: int(_env("REPOSNIFFER_SEARCH_PER_PAGE", "50") or "50")
    )
    repo_cache_ttl_hours: float = field(
        default_factory=lambda: float(_env("REPOSNIFFER_REPO_TTL_HOURS", "168") or "168")
    )
    query_cache_ttl_hours: float = field(
        default_factory=lambda: float(_env("REPOSNIFFER_QUERY_TTL_HOURS", "24") or "24")
    )

    @property
    def db_path(self) -> Path:
        explicit = _env("REPOSNIFFER_DB")
        if explicit:
            return Path(explicit)
        base = Path(
            _env("XDG_CACHE_HOME", str(Path.home() / ".cache")) or str(Path.home() / ".cache")
        )
        return base / "reposniffer" / "reposniffer.db"

    @property
    def is_api_embedding(self) -> bool:
        return self.embed_backend.lower() in {"api", "remote", "openai"}

    def summary(self) -> dict:
        return {
            "embed_backend": "api" if self.is_api_embedding else "local",
            "embed_model": self.embed_api_model if self.is_api_embedding else self.embed_model,
            "github_token_set": bool(self.github_token),
            "db": str(self.db_path),
            "github_api_base": self.github_api_base,
        }
