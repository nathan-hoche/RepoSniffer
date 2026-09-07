# Eval golden set: query -> expected repo(s) that SHOULD rank highly.
# Used by `uv run python -m reposniffer.eval.run` to measure retrieval quality.
# Add queries covering the supported question types:
#   - feature ("markdown editor with live preview")
#   - tech pattern ("websocket rate limiting")
#   - narrow library ("PDF generation from HTML")
GOLDEN = [
    {
        "query": "markdown editor with live preview",
        "expected": ["testcorp/markdown-live"],
        "intent": "adopt",
    },
    {
        "query": "websocket rate limiting",
        "expected": ["testcorp/websocket-throttle"],
        "intent": "study",
    },
]
