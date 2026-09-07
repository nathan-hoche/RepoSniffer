from __future__ import annotations

from reposniffer.config import Settings
from reposniffer.engine.github import GitHub
from tests.conftest import FakeTransport


def test_github_client_uses_fake_transport():
    settings = Settings(github_api_base="https://api.github.com")
    github = GitHub(settings, transport=FakeTransport())
    items = github.search_repos("anything", per_page=25)
    assert len(items) == 3
