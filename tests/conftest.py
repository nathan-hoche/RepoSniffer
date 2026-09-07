from __future__ import annotations

from typing import Any

import httpx
import pytest

from reposniffer.cache import Store
from reposniffer.config import Settings
from reposniffer.engine.github import GitHub
from reposniffer.engine.search import Engine

SAMPLE_REPOS = [
    {
        "full_name": "testcorp/markdown-live",
        "html_url": "https://github.com/testcorp/markdown-live",
        "description": "Markdown editor with live preview",
        "stargazers_count": 12000,
        "forks_count": 800,
        "language": "Python",
        "license": {"spdx_id": "MIT"},
        "archived": False,
        "pushed_at": "2026-08-01T12:00:00Z",
        "default_branch": "main",
        "readme": "## markdown-live\nA markdown editor with **live preview** as you type. Great for docs.",
    },
    {
        "full_name": "testcorp/websocket-throttle",
        "html_url": "https://github.com/testcorp/websocket-throttle",
        "description": "WebSocket rate limiting",
        "stargazers_count": 300,
        "forks_count": 20,
        "language": "Go",
        "license": {"spdx_id": "Apache-2.0"},
        "archived": False,
        "pushed_at": "2025-01-15T12:00:00Z",
        "default_branch": "main",
        "readme": "# websocket-throttle\nWebSocket rate limiting for high-throughput servers.",
    },
    {
        "full_name": "dead/old-project",
        "html_url": "https://github.com/dead/old-project",
        "description": "Something completely unrelated about databases",
        "stargazers_count": 50,
        "forks_count": 5,
        "language": "Python",
        "license": {"spdx_id": "GPL-3.0"},
        "archived": True,
        "pushed_at": "2021-03-01T12:00:00Z",
        "default_branch": "master",
        "readme": "# old-project\nUnrelated database thing.",
    },
]


class FakeTransport(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url.startswith("https://api.github.com/search/repositories"):
            return httpx.Response(200, json={"items": SAMPLE_REPOS})
        if "/readme" in url:
            for repo in SAMPLE_REPOS:
                if repo["full_name"].replace("/", "/") in url:
                    return httpx.Response(200, content=repo["readme"])
            return httpx.Response(404)
        if url.startswith("https://api.github.com/repos/"):
            name = url.split("/repos/")[1].split("?")[0]
            for repo in SAMPLE_REPOS:
                if repo["full_name"] == name:
                    return httpx.Response(
                        200, json={k: v for k, v in repo.items() if k != "readme"}
                    )
            return httpx.Response(404)
        return httpx.Response(500)


class FakeEmbedder:
    model_name = "fake-model"
    dimension = 4

    def embed(self, texts: list[str]) -> Any:
        import numpy as np

        rows = []
        for text in texts:
            if "markdown" in text.lower() or "preview" in text.lower():
                rows.append([1.0, 0.0, 0.0, 0.0])
            elif "websocket" in text.lower() or "rate limit" in text.lower():
                rows.append([0.0, 1.0, 0.0, 0.0])
            elif "database" in text.lower():
                rows.append([0.0, 0.0, 1.0, 0.0])
            else:
                rows.append([0.0, 0.0, 0.0, 1.0])
        arr = np.asarray(rows, dtype=np.float32)
        arr = arr / np.linalg.norm(arr, axis=1, keepdims=True)
        return arr


@pytest.fixture()
def store(tmp_path) -> Store:
    return Store(tmp_path / "test.db")


@pytest.fixture()
def github() -> GitHub:
    settings = Settings(github_api_base="https://api.github.com", repo_cache_ttl_hours=0.001)
    return GitHub(settings, transport=FakeTransport())


@pytest.fixture()
def engine(store, github) -> Engine:
    settings = Settings(
        github_api_base="https://api.github.com",
        repo_cache_ttl_hours=0.001,
        query_cache_ttl_hours=0.001,
    )
    return Engine(store, github, FakeEmbedder(), settings)
