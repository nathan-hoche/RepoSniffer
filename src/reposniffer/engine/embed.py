from __future__ import annotations

from typing import Protocol

import numpy as np


class Embedder(Protocol):
    @property
    def model_name(self) -> str: ...

    @property
    def dimension(self) -> int: ...

    def embed(self, texts: list[str]) -> np.ndarray: ...


def l2_normalize(matrix: np.ndarray) -> np.ndarray:
    arr = np.asarray(matrix, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return arr / norms


class FastEmbedEmbedder:
    def __init__(self, model_name: str) -> None:
        from fastembed import TextEmbedding  # lazy: onnxruntime import is heavy

        self._model_name = model_name
        self._te = TextEmbedding(model_name=model_name)
        seed = list(self._te.embed(["seed"]))
        self._dimension = len(seed[0]) if seed else 0

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.vstack([np.asarray(v, dtype=np.float32) for v in self._te.embed(texts)])
        return l2_normalize(vectors)


class ApiEmbedder:
    def __init__(
        self,
        base_url: str,
        api_key: str | None,
        model: str,
        default_dimension: int,
        timeout: float = 20.0,
    ) -> None:
        import httpx

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._model = model
        self._dimension = default_dimension
        self._http = httpx.Client(base_url=base_url, headers=headers, timeout=timeout)

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> np.ndarray:

        resp = self._http.post(
            "/embeddings",
            json={"model": self._model, "input": texts},
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"Embeddings API {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        items = data.get("data") or []
        rows: list[list[float]] = []
        for item in items:
            emb = item.get("embedding")
            if emb:
                rows.append(list(emb))
        arr = np.asarray(rows, dtype=np.float32)
        self._dimension = arr.shape[1] if arr.ndim == 2 else self._dimension
        return l2_normalize(arr)
