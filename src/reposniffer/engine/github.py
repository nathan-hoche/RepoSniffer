from __future__ import annotations

import hashlib
import re
from typing import Any

import httpx

from reposniffer.config import Settings


class GitHubError(Exception):
    pass


class RateLimitError(GitHubError):
    def __init__(self, message: str, reset_at: int | None = None) -> None:
        super().__init__(message)
        self.reset_at = reset_at


class GitHub:
    def __init__(
        self,
        settings: Settings,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        self._settings = settings
        self._http = httpx.Client(
            base_url=settings.github_api_base,
            headers=headers,
            timeout=settings.request_timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._http.close()

    def _get(self, path: str, **params: Any) -> Any:
        resp = self._http.get(path, params=params)
        if resp.status_code == 403 and "rate limit" in (
            resp.headers.get("x-ratelimit-remaining", "")
        ):
            reset = int(resp.headers.get("x-ratelimit-reset", "0") or 0)
            raise RateLimitError(
                "GitHub API rate limit reached; set GITHUB_TOKEN or retry later", reset
            )
        if resp.status_code >= 400:
            raise GitHubError(f"GitHub API {resp.status_code} for {path}: {resp.text[:200]}")
        return resp.json()

    def search_repos(self, query: str, per_page: int) -> list[dict[str, Any]]:
        data = self._get("/search/repositories", q=query, per_page=per_page)
        return list(data.get("items", []))

    def repo(self, owner_repo: str) -> dict[str, Any]:
        return self._get(f"/repos/{owner_repo}")

    def readme(self, owner_repo: str) -> str | None:
        resp = self._http.get(
            f"/repos/{owner_repo}/readme",
            headers={"Accept": "application/vnd.github.raw+json"},
        )
        if resp.status_code == 404:
            return None
        if resp.status_code >= 400:
            raise GitHubError(f"GitHub API {resp.status_code} fetching README for {owner_repo}")
        return resp.text


def build_search_query(
    query: str,
    language: str | None = None,
    license_key: str | None = None,
    min_stars: int | None = None,
    include_archived: bool = False,
) -> str:
    tokens: list[str] = []
    q = query.strip()
    if "in:" not in q and "q=" not in q:
        tokens.append(q)
        tokens.append("in:readme")
    else:
        tokens.append(q)
    if language:
        tokens.append(f"language:{language}")
    if license_key:
        tokens.append(f"license:{license_key}")
    if min_stars is not None:
        tokens.append(f"stars:>={min_stars}")
    if not include_archived:
        tokens.append("archived:false")
    return " ".join(tokens)


def strip_markdown(text: str) -> str:
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[#*_>~|]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def excerpt(readme: str, limit: int = 500) -> str:
    clean = strip_markdown(readme)
    return clean[:limit]


def query_cache_key(
    query: str, language: str | None, license_key: str | None, min_stars: int | None
) -> str:
    raw = "|".join([query, language or "", license_key or "", str(min_stars or "")])
    return hashlib.sha256(raw.encode()).hexdigest()


def short_owner_repo(full_name: str) -> str:
    return full_name
