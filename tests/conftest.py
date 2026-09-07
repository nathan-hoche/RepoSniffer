from __future__ import annotations

import pytest

from reposniffer.cache import Store
from reposniffer.config import Settings
from reposniffer.engine.github import GitHub
from reposniffer.engine.search import Engine
from reposniffer.testing import FakeEmbedder, FakeTransport


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
