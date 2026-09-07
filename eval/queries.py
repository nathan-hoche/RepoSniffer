from __future__ import annotations

GOLDEN: list[dict] = [
    {
        "query": "markdown editor with live preview",
        "expected": ["ianstormtaylor/slate", "codex-team/editor.js"],
        "intent": "adopt",
    },
    {
        "query": "PDF generation from HTML",
        "expected": ["Kozea/WeasyPrint", "pdfkit/pdfkit"],
        "intent": "adopt",
    },
    {
        "query": "HTTP client for Python with async support",
        "expected": ["encode/httpx", "psf/requests"],
        "intent": "adopt",
    },
    {
        "query": "build CLI applications from type hints",
        "expected": ["fastapi/typer", "click/click"],
        "intent": "adopt",
    },
    {
        "query": "terminal colors and rich formatting for Python",
        "expected": ["Textualize/rich", "blessed/termcolor"],
        "intent": "study",
    },
    {
        "query": "ASGI web framework with automatic API documentation",
        "expected": ["fastapi/fastapi", "encode/starlette"],
        "intent": "study",
    },
]
