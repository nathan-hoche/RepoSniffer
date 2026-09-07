from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = [sys.executable, "-m", "reposniffer.mcp.server"]


def check() -> None:
    env = {"REPOSNIFFER_FAKE_ENGINE": "1", "GITHUB_TOKEN": ""}
    proc = subprocess.Popen(
        SERVER,
        cwd=ROOT,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:

        def send(obj: dict) -> None:
            assert proc.stdin is not None
            proc.stdin.write(json.dumps(obj) + "\n")
            proc.stdin.flush()

        def read(timeout: float = 30.0) -> dict:
            assert proc.stdout is not None
            import select

            ready, _, _ = select.select([proc.stdout], [], [], timeout)
            if not ready:
                raise TimeoutError(f"no MCP response within {timeout}s")
            return json.loads(proc.stdout.readline())

        send(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "ci-check", "version": "1.0"},
                },
            }
        )
        init = read()
        assert init["result"]["serverInfo"]["name"] == "reposniffer", init
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = read()["result"]["tools"]
        names = {t["name"]: t for t in tools}
        assert set(names) == {"find_repos", "repo_intel", "health"}, names
        find_schema = names["find_repos"]["inputSchema"].get("properties", {})
        assert set(find_schema) >= {
            "query",
            "intent",
            "language",
            "license",
            "min_stars",
            "top_k",
            "include_archived",
        }, find_schema
        print("tools/list: OK (find_repos, repo_intel, health)")

        send(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "health", "arguments": {}},
            }
        )
        health = read()
        assert not health["result"].get("isError"), health
        print("tools/call health: OK")

        send(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "find_repos",
                    "arguments": {"query": "markdown editor with live preview", "top_k": 3},
                },
            }
        )
        result = read(120)
        assert not result["result"].get("isError"), result
        payload = json.loads(result["result"]["content"][0]["text"])
        assert "error" not in payload, payload
        assert payload["results"], "find_repos returned no results"
        assert payload["results"][0]["full_name"] == "testcorp/markdown-live", payload
        print("tools/call find_repos: OK (testcorp/markdown-live #1)")

        send(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "repo_intel",
                    "arguments": {"owner_repo": "testcorp/markdown-live"},
                },
            }
        )
        intel = read(120)
        assert not intel["result"].get("isError"), intel
        print("tools/call repo_intel: OK")

        print("MCP check passed")
    finally:
        proc.kill()


if __name__ == "__main__":
    try:
        check()
    except Exception:
        import sys

        sys.exit(1)
