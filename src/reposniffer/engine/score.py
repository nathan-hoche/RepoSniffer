from __future__ import annotations

import math
import time
from typing import Any, Literal

from reposniffer.engine.github import tokenize

Intent = Literal["adopt", "study"]

LICENSE_CATEGORIES: dict[str, str] = {
    "MIT": "permissive",
    "Apache-2.0": "permissive",
    "BSD-2-Clause": "permissive",
    "BSD-3-Clause": "permissive",
    "ISC": "permissive",
    "0BSD": "permissive",
    "Unlicense": "permissive",
    "WTFPL": "permissive",
    "Python-2.0": "permissive",
    "MPL-2.0": "weak-copyleft",
    "LGPL-2.1": "weak-copyleft",
    "LGPL-3.0": "weak-copyleft",
    "EPL-1.0": "weak-copyleft",
    "EPL-2.0": "weak-copyleft",
    "GPL-2.0": "strong-copyleft",
    "GPL-3.0": "strong-copyleft",
    "AGPL-3.0": "strong-copyleft",
}


def license_info(spdx: str | None) -> dict[str, Any]:
    if not spdx or spdx in {"NOASSERTION", "Other", "SEE LICENSE IN LICENSE"}:
        return {
            "category": "unknown",
            "dependency_safe": False,
            "note": "no recognized license — verify before depending",
        }
    category = LICENSE_CATEGORIES.get(spdx, "unknown")
    if category == "permissive":
        return {"category": category, "dependency_safe": True, "note": f"{spdx}: safe to depend on"}
    if category == "weak-copyleft":
        return {
            "category": category,
            "dependency_safe": False,
            "note": f"{spdx}: weak copyleft — usually OK for linking, review terms",
        }
    if category == "strong-copyleft":
        return {
            "category": category,
            "dependency_safe": False,
            "note": f"{spdx}: strong copyleft — may force license on your derivative work",
        }
    return {
        "category": category,
        "dependency_safe": False,
        "note": f"{spdx}: verify the license terms",
    }


def lexical_overlap(query: str, text: str) -> float:
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return 0.0
    text_tokens = set(tokenize(text))
    if not text_tokens:
        return 0.0
    return len(query_tokens & text_tokens) / len(query_tokens)


def _days_since(iso_timestamp: str) -> float:
    if not iso_timestamp:
        return float("inf")
    try:
        parsed = time.mktime(time.strptime(iso_timestamp[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return float("inf")
    return max(0.0, (time.time() - parsed) / 86400.0)


def activity_score(iso_timestamp: str) -> float:
    days = _days_since(iso_timestamp)
    if math.isinf(days):
        return 0.0
    return math.exp(-math.log(2) * days / 182.0)


def popularity_score(stars: int, forks: int) -> float:
    star = min(math.log10(1 + stars) / 4.0, 1.0)
    fork = min(math.log10(1 + forks) / 3.0, 1.0)
    return 0.7 * star + 0.3 * fork


def quality_score(
    meta: dict[str, Any],
    activity_weight: float = 0.4,
    license_weight: float = 0.2,
    popularity_weight: float = 0.4,
) -> dict[str, float]:
    archived = bool(meta.get("archived", False))
    lic = (
        (meta.get("license") or {}).get("spdx_id")
        if isinstance(meta.get("license"), dict)
        else None
    )
    stars = int(meta.get("stargazers_count", 0))
    forks = int(meta.get("forks_count", 0))
    pushed = str(meta.get("pushed_at", ""))

    activity = activity_score(pushed)
    license_ok = 1.0 if lic else 0.0
    popularity = popularity_score(stars, forks)
    quality = (
        activity_weight * activity + license_weight * license_ok + popularity_weight * popularity
    )
    if archived:
        quality *= 0.25
    return {
        "activity": round(activity, 3),
        "license": license_ok,
        "popularity": round(popularity, 3),
        "quality": round(quality, 3),
    }


def intent_weights(intent: Intent) -> dict[str, float]:
    if intent == "study":
        return {"semantic": 0.75, "quality": 0.25}
    return {"semantic": 0.5, "quality": 0.5}


def combine_score(semantic: float, quality: float, intent: Intent) -> float:
    w = intent_weights(intent)
    return w["semantic"] * semantic + w["quality"] * quality
