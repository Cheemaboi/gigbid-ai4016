"""Small deterministic retrieval facade used in the demo and tests."""
from __future__ import annotations
from agent.handoffs import EvidenceItem


def normalise(text: str) -> set[str]:
    return {part.strip(".,:;!?()[]").lower() for part in text.split() if len(part) > 2}


def retrieve(requirements: list[str], corpus: list[dict], variant: str = "v2_hybrid", k: int = 5) -> list[EvidenceItem]:
    query = normalise(" ".join(requirements))
    scored = []
    for item in corpus:
        fields = " ".join([item["title"], item["content"], " ".join(item["skills"])])
        overlap = len(query & normalise(fields))
        outcome_bonus = 2 if variant in {"v4_outcome", "v8_corrective", "v2_hybrid"} and item["outcome"] == "won" else 0
        scored.append((overlap + outcome_bonus, item))
    return [EvidenceItem(id=item["id"], title=item["title"], excerpt=item["content"], skills=item["skills"], outcome=item["outcome"])
            for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:k]]

