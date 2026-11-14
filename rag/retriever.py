"""Transparent, offline retrieval variants used by GigBid.

They are deliberately lightweight so a reviewer can reproduce them without a hosted
embedding API. Each variant has different ranking behaviour; none is presented as a
trained semantic retriever or cross-encoder.
"""
from __future__ import annotations

import re
from collections.abc import Callable

from agent.handoffs import EvidenceItem

TOKEN = re.compile(r"[a-z0-9+#.]{2,}")


def normalise(text: str) -> set[str]:
    return set(TOKEN.findall(text.lower()))


def _fields(item: dict) -> set[str]:
    return normalise(" ".join([item["title"], item["content"], " ".join(item["skills"])]))


def _requirement_coverage(requirements: list[str], item: dict) -> float:
    if not requirements:
        return 0.0
    fields = _fields(item)
    covered = sum(bool(normalise(requirement) & fields) for requirement in requirements)
    return covered / len(requirements)


def _lexical_score(query: set[str], item: dict) -> float:
    fields = _fields(item)
    return len(query & fields) / max(1, len(query))


def _skill_score(requirements: list[str], item: dict) -> float:
    wanted = {token for requirement in requirements for token in normalise(requirement)}
    skills = normalise(" ".join(item["skills"]))
    return len(wanted & skills) / max(1, len(wanted))


def _rank(corpus: list[dict], scorer: Callable[[dict], float]) -> list[dict]:
    return [item for _, item in sorted(((scorer(item), item) for item in corpus), key=lambda pair: (-pair[0], pair[1]["id"]))]


def _v0_naive(query: set[str], requirements: list[str], corpus: list[dict]) -> list[dict]:
    """Fixed lexical overlap baseline."""
    return _rank(corpus, lambda item: _lexical_score(query, item))


def _v1_decompose(query: set[str], requirements: list[str], corpus: list[dict]) -> list[dict]:
    """Scores each requirement independently before aggregating coverage."""
    return _rank(corpus, lambda item: _requirement_coverage(requirements, item))


def _v2_hybrid(query: set[str], requirements: list[str], corpus: list[dict]) -> list[dict]:
    """Combines description-token overlap with explicit portfolio-skill matches."""
    return _rank(corpus, lambda item: 0.55 * _lexical_score(query, item) + 0.45 * _skill_score(requirements, item))


def _v3_rerank(query: set[str], requirements: list[str], corpus: list[dict]) -> list[dict]:
    """Candidate retrieval followed by a stricter deterministic coverage rerank."""
    candidates = _v2_hybrid(query, requirements, corpus)[: min(len(corpus), 15)]
    return _rank(candidates, lambda item: 0.25 * _lexical_score(query, item) + 0.75 * _requirement_coverage(requirements, item))


def _v4_outcome(query: set[str], requirements: list[str], corpus: list[dict]) -> list[dict]:
    """Reranks coverage candidates with a bounded prior-outcome preference."""
    candidates = _v3_rerank(query, requirements, corpus)
    return _rank(candidates, lambda item: _requirement_coverage(requirements, item) + (0.12 if item.get("outcome") == "won" else 0.0))


def _v8_corrective(query: set[str], requirements: list[str], corpus: list[dict], k: int) -> list[dict]:
    """Greedily corrects coverage gaps after the first hybrid retrieval pass."""
    candidates = _v2_hybrid(query, requirements, corpus)
    selected: list[dict] = []
    covered: set[str] = set()
    required = {token for requirement in requirements for token in normalise(requirement)}
    for _ in range(min(k, len(candidates))):
        best = max(
            (item for item in candidates if item not in selected),
            key=lambda item: (len((_fields(item) & required) - covered), _lexical_score(query, item), item["id"]),
        )
        selected.append(best)
        covered.update(_fields(best) & required)
    return selected


VARIANTS = {"v0_naive", "v1_decompose", "v2_hybrid", "v3_rerank", "v4_outcome", "v8_corrective"}


def retrieve(requirements: list[str], corpus: list[dict], variant: str = "v2_hybrid", k: int = 5) -> list[EvidenceItem]:
    """Retrieve typed evidence using one named, reproducible ranking strategy."""
    if variant not in VARIANTS:
        raise ValueError(f"Unknown retrieval variant: {variant}")
    query = normalise(" ".join(requirements))
    if variant == "v0_naive":
        ranked = _v0_naive(query, requirements, corpus)
    elif variant == "v1_decompose":
        ranked = _v1_decompose(query, requirements, corpus)
    elif variant == "v2_hybrid":
        ranked = _v2_hybrid(query, requirements, corpus)
    elif variant == "v3_rerank":
        ranked = _v3_rerank(query, requirements, corpus)
    elif variant == "v4_outcome":
        ranked = _v4_outcome(query, requirements, corpus)
    else:
        ranked = _v8_corrective(query, requirements, corpus, k)
    return [EvidenceItem(id=item["id"], title=item["title"], excerpt=item["content"], skills=item["skills"], outcome=item["outcome"])
            for item in ranked[:k]]
