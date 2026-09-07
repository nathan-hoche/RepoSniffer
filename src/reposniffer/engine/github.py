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
        if resp.status_code == 403 and resp.headers.get("x-ratelimit-remaining") == "0":
            reset = int(resp.headers.get("x-ratelimit-reset", "0") or 0)
            raise RateLimitError(
                "GitHub API rate limit reached; set GITHUB_TOKEN or retry later", reset
            )
        if resp.status_code >= 400:
            raise GitHubError(f"GitHub API {resp.status_code} fetching README for {owner_repo}")
        return resp.text


def _filter_suffix(
    language: str | None,
    license_key: str | None,
    min_stars: int | None,
    include_archived: bool,
) -> list[str]:
    tokens: list[str] = []
    if language:
        tokens.append(f"language:{language}")
    if license_key:
        tokens.append(f"license:{license_key}")
    if min_stars is not None:
        tokens.append(f"stars:>={min_stars}")
    if not include_archived:
        tokens.append("archived:false")
    return tokens


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
        keywords = " ".join(tokenize(q)) or q
        tokens.append(keywords)
        tokens.append("in:readme")
    else:
        tokens.append(q)
    tokens.extend(_filter_suffix(language, license_key, min_stars, include_archived))
    return " ".join(tokens)


TOPIC_WORDS = {
    "pdf",
    "html",
    "css",
    "json",
    "yaml",
    "xml",
    "csv",
    "markdown",
    "api",
    "cli",
    "http",
    "websocket",
    "graphql",
    "rest",
    "sql",
    "docker",
    "kubernetes",
    "auth",
    "oauth",
    "python",
    "javascript",
    "typescript",
    "rust",
    "go",
    "java",
    "editor",
    "converter",
    "compiler",
    "framework",
    "library",
    "client",
    "server",
    "database",
    "async",
    "terminal",
    "tui",
    "image",
    "video",
    "audio",
}


def build_topic_query(
    query: str,
    language: str | None = None,
    license_key: str | None = None,
    min_stars: int | None = None,
    include_archived: bool = False,
) -> str | None:
    q = query.strip()
    if "in:" in q or "q=" in q:
        return None
    topics = [w for w in tokenize(q) if w in TOPIC_WORDS]
    if len(topics) < 2:
        return None
    tokens: list[str] = [" ".join(topics)]
    tokens.extend(f"topic:{t}" for t in topics[:2])
    tokens.extend(_filter_suffix(language, license_key, min_stars, include_archived))
    return " ".join(tokens)


def is_curated_list(meta: dict[str, Any]) -> bool:
    name = str(meta.get("name") or "").lower()
    description = str(meta.get("description") or "").lower()
    topics = [str(t).lower() for t in (meta.get("topics") or [])]
    if "awesome" in name or "awesome" in description:
        return True
    if "awesome-list" in " ".join(topics):
        return True
    if name.startswith("awesome-"):
        return True
    return False


def filter_curated_lists(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in items if not is_curated_list(item)]


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


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "your",
    "you",
    "are",
    "has",
    "have",
    "was",
    "were",
    "will",
    "can",
    "not",
    "but",
    "its",
    "it's",
    "into",
    "over",
    "under",
    "than",
    "then",
    "them",
    "they",
    "their",
    "which",
    "who",
    "what",
    "when",
    "where",
    "how",
    "all",
    "any",
    "some",
    "also",
    "very",
    "just",
    "more",
    "most",
    "such",
    "only",
    "own",
    "same",
    "too",
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) >= 2]


def front_matter(text: str, limit: int = 1000) -> str:
    return strip_markdown(text)[:limit]


def text_for_embedding(description: str | None, readme: str | None, limit: int = 1000) -> str:
    parts: list[str] = []
    if description:
        parts.append(description.strip())
    if readme:
        parts.append(front_matter(readme, limit))
    return "\n".join(p for p in parts if p)


def best_snippet(readme: str, query: str, limit: int = 500) -> str:
    clean = strip_markdown(readme)
    if not clean:
        return ""
    q = set(tokenize(query))
    if not q:
        return clean[:limit]
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", clean) if s.strip()]
    if not sentences:
        return clean[:limit]
    scored = sorted(
        ((sum(1 for t in tokenize(s) if t in q), s) for s in sentences),
        key=lambda pair: pair[0],
        reverse=True,
    )
    best_score, best = scored[0]
    if best_score == 0:
        return clean[:limit]
    idx = clean.find(best)
    start = max(0, idx - limit // 2)
    return clean[start : start + limit].strip()


def query_cache_key(
    query: str, language: str | None, license_key: str | None, min_stars: int | None
) -> str:
    raw = "|".join([query, language or "", license_key or "", str(min_stars or "")])
    return hashlib.sha256(f"{QUERY_CACHE_VERSION}|{raw}".encode()).hexdigest()


QUERY_CACHE_VERSION = "v4"


def short_owner_repo(full_name: str) -> str:
    return full_name
