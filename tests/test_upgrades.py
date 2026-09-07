from __future__ import annotations

from reposniffer.engine.github import best_snippet, text_for_embedding, tokenize
from reposniffer.engine.score import lexical_overlap, license_info


def test_tokenize_drops_stopwords_and_singles():
    assert tokenize("The markdown editor for you") == ["markdown", "editor"]


def test_license_categories():
    assert license_info("MIT")["category"] == "permissive"
    assert license_info("MIT")["dependency_safe"] is True
    assert license_info("AGPL-3.0")["category"] == "strong-copyleft"
    assert license_info("AGPL-3.0")["dependency_safe"] is False
    assert license_info("LGPL-3.0")["category"] == "weak-copyleft"
    assert license_info(None)["category"] == "unknown"
    assert license_info("NOASSERTION")["category"] == "unknown"


def test_lexical_overlap():
    assert (
        lexical_overlap("markdown editor live preview", "a markdown editor with live preview") > 0
    )
    assert lexical_overlap("crypto wallet", "database toolkit") == 0


def test_text_for_embedding_uses_description_and_front_matter():
    text = text_for_embedding("A markdown editor", "## Header\nLong body about other things" * 200)
    assert text.startswith("A markdown editor")
    assert len(text) < 2500  # front matter truncated


def test_best_snippet_finds_matching_sentence():
    readme = (
        "# x\nIntro about unrelated stuff.\nThis is a markdown editor with live preview.\nFooter."
    )
    snippet = best_snippet(readme, "markdown editor live preview")
    assert "markdown editor with live preview" in snippet


def test_best_snippet_falls_back_to_head():
    snippet = best_snippet("# just a title\nNo overlap here.", "crypto wallet")
    assert "No overlap" in snippet
