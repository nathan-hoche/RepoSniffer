---
title: Python API
description: Reference for the Python API.
---

RepoSniffer is primarily used as a CLI and MCP server, but everything is importable.

## `build_engine()`

```python
from reposniffer.engine.search import build_engine

engine = build_engine()            # defaults from env vars
engine.close()
```

`build_engine` wires together the SQLite cache, GitHub client, and embedder. You can
inject any of them for tests or custom setups:

```python
build_engine(settings=..., store=..., github=..., embedder=...)
```

## `Engine.search()`

```python
results = engine.search(
    query="markdown editor with live preview",
    language="python",
    intent="adopt",          # "adopt" | "study"
    top_k=5,
    include_archived=False,
)
```

Returns a list of result dicts with: `full_name`, `stars`, `language`, `license`,
`license_category`, `archived`, `pushed_at`, `as_of`, `flags`, `semantic`, `lexical`,
`relevance`, `quality` (breakdown), `overall`, `snippet`, `recommendation`.

## `Engine.repo_intel()`

```python
intel = engine.repo_intel("ianstormtaylor/slate", top_k=2)
```

Verifies a single repo and returns a status verdict plus alternatives.

## `Settings`

```python
from reposniffer.config import Settings

s = Settings()
s.github_token        # GITHUB_TOKEN or gh fallback
s.embed_backend       # "local" | "api"
s.db_path             # sqlite cache path
```

## Embedder protocol

Custom embedding backends implement three members:

```python
class Embedder(Protocol):
    model_name: str
    dimension: int
    def embed(self, texts: list[str]) -> np.ndarray: ...
```

See `reposniffer.engine.embed` for the local `FastEmbedEmbedder` and `ApiEmbedder`
implementations.