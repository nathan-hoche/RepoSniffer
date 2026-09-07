from __future__ import annotations

from typing import Any

import numpy as np

from reposniffer.cache import Store
from reposniffer.config import Settings
from reposniffer.engine.embed import Embedder, l2_normalize
from reposniffer.engine.github import (
    GitHub,
    build_search_query,
    excerpt,
    query_cache_key,
)
from reposniffer.engine.score import Intent, combine_score, intent_weights, quality_score


def build_engine(
    settings: Settings | None = None,
    store: Store | None = None,
    github: GitHub | None = None,
    embedder: Embedder | None = None,
) -> Engine:
    settings = settings or Settings()
    store = store or Store(settings.db_path)
    github = github or GitHub(settings)
    if embedder is None:
        if settings.is_api_embedding:
            from reposniffer.engine.embed import ApiEmbedder

            embedder = ApiEmbedder(
                base_url=settings.embed_api_base,
                api_key=settings.embed_api_key,
                model=settings.embed_api_model,
                default_dimension=settings.embed_dimension,
                timeout=settings.request_timeout,
            )
        else:
            from reposniffer.engine.embed import FastEmbedEmbedder

            embedder = FastEmbedEmbedder(settings.embed_model)
    return Engine(store, github, embedder, settings)


class Engine:
    def __init__(
        self,
        store: Store,
        github: GitHub,
        embedder: Embedder,
        settings: Settings,
    ) -> None:
        self._store = store
        self._github = github
        self._embedder = embedder
        self._settings = settings

    @property
    def model_name(self) -> str:
        return self._embedder.model_name

    def close(self) -> None:
        try:
            self._store.close()
        finally:
            self._github.close()

    def search(
        self,
        query: str,
        language: str | None = None,
        license_key: str | None = None,
        min_stars: int | None = None,
        intent: Intent = "adopt",
        top_k: int = 5,
        include_archived: bool = False,
    ) -> list[dict[str, Any]]:
        query_vec = self._embedder.embed([query])[0]
        gh_query = build_search_query(
            query,
            language=language,
            license_key=license_key,
            min_stars=min_stars,
            include_archived=include_archived,
        )
        key = query_cache_key(query, language, license_key, min_stars)

        candidates = self._store.get_query(key, self._settings.query_cache_ttl_hours)
        if candidates is None:
            candidates = self._github.search_repos(gh_query, self._settings.search_per_page)
            self._store.put_query(key, candidates)

        metas = self._finalize_metas(candidates)
        texts: list[str] = []
        for meta in metas:
            readme = meta.get("readme")
            texts.append(readme if readme else str(meta.get("description") or ""))

        vectors: dict[str, np.ndarray] = {}
        missing: list[tuple[str, int]] = []
        for i, meta in enumerate(metas):
            emb = self._store.get_embedding(meta["full_name"], self.model_name)
            if emb is None:
                missing.append((meta["full_name"], i))
            else:
                vectors[meta["full_name"]] = emb
        if missing:
            batch_texts = [texts[idx] for _, idx in missing]
            batch = l2_normalize(self._embedder.embed(batch_texts))
            for (name, _), vec in zip(missing, batch, strict=True):
                self._store.put_embedding(name, self.model_name, vec)
                vectors[name] = vec

        results: list[dict[str, Any]] = []
        for meta in metas:
            vec = vectors.get(meta["full_name"])
            semantic = float(np.dot(query_vec, vec)) if vec is not None and np.any(vec) else 0.0
            quality = quality_score(meta)
            overall = combine_score(semantic, quality["quality"], intent)
            readme = meta.get("readme")
            results.append(self._render(meta, semantic, quality, overall, readme, intent))

        results.sort(key=lambda r: r["overall"], reverse=True)
        for rank, result in enumerate(results, start=1):
            result["rank"] = rank
        return results[:top_k]

    def repo_intel(
        self,
        owner_repo: str,
        query: str | None = None,
        top_k: int = 2,
    ) -> dict[str, Any]:
        meta = self._finalize_metas([self._github.repo(owner_repo)])[0]
        query_text = query or str(meta.get("description") or meta.get("full_name"))
        query_vec = self._embedder.embed([query_text])[0]
        readme = meta.get("readme")
        text = readme if readme else str(meta.get("description") or "")
        vec = self._embedder.embed([text])[0]
        semantic = float(np.dot(query_vec, vec)) if np.any(vec) else 0.0
        quality = quality_score(meta)
        overall = combine_score(semantic, quality["quality"], "adopt")

        alternatives = [
            r
            for r in self.search(
                query=query_text,
                language=meta.get("language"),
                intent="adopt",
                top_k=top_k + 1,
            )
            if r["full_name"] != owner_repo
        ][:top_k]

        status = "avoid: archived"
        if not meta.get("archived"):
            if quality["activity"] >= 0.5 and quality["license"]:
                status = "healthy and licensed"
            elif quality["activity"] >= 0.5:
                status = "healthy, missing license"
            else:
                status = "stale (low recent activity)"

        return {
            "full_name": owner_repo,
            "html_url": meta.get("html_url"),
            "description": meta.get("description"),
            "stars": meta.get("stargazers_count"),
            "forks": meta.get("forks_count"),
            "language": meta.get("language"),
            "license": (meta.get("license") or {}).get("spdx_id")
            if isinstance(meta.get("license"), dict)
            else None,
            "archived": meta.get("archived"),
            "pushed_at": meta.get("pushed_at"),
            "has_readme": bool(readme),
            "status": status,
            "semantic": round(semantic, 3),
            "quality": quality,
            "overall": round(overall, 3),
            "alternatives": alternatives,
        }

    def _finalize_metas(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        metas: list[dict[str, Any]] = []
        for meta in candidates:
            cached = self._store.get_repo(meta["full_name"], self._settings.repo_cache_ttl_hours)
            if cached is not None:
                metas.append(cached)
                continue
            readme = self._github.readme(meta["full_name"])
            merged = {**meta, **{"readme": readme}}
            self._store.put_repo(merged, readme)
            metas.append(merged)
        return metas

    def _render(
        self,
        meta: dict[str, Any],
        semantic: float,
        quality: dict[str, float],
        overall: float,
        readme: str | None,
        intent: Intent,
    ) -> dict[str, Any]:
        lic = (
            (meta.get("license") or {}).get("spdx_id")
            if isinstance(meta.get("license"), dict)
            else None
        )
        evidence = excerpt(readme) if readme else str(meta.get("description") or "")
        if meta.get("archived"):
            recommendation = "avoid (archived)"
        elif quality["quality"] >= 0.55 and semantic >= 0.4:
            recommendation = "strong candidate"
        elif semantic >= 0.35:
            recommendation = "promising; check activity/license"
        else:
            recommendation = "weak match"
        return {
            "rank": 0,
            "full_name": meta["full_name"],
            "html_url": meta.get("html_url"),
            "description": meta.get("description"),
            "stars": meta.get("stargazers_count"),
            "forks": meta.get("forks_count"),
            "language": meta.get("language"),
            "license": lic,
            "archived": meta.get("archived"),
            "pushed_at": meta.get("pushed_at"),
            "default_branch": meta.get("default_branch"),
            "has_readme": bool(readme),
            "semantic": round(semantic, 3),
            "activity": quality["activity"],
            "license_score": quality["license"],
            "popularity": quality["popularity"],
            "quality": quality["quality"],
            "overall": round(overall, 3),
            "evidence": evidence[:600],
            "recommendation": recommendation,
            "weights": intent_weights(intent),
        }
