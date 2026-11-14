from __future__ import annotations
from agent.handoffs import ClaimCheck, EvidenceItem


def verify_claims(draft: str, evidence: list[EvidenceItem]) -> list[ClaimCheck]:
    """Conservative verifier: only claims tied to a known skill/project pass."""
    checks: list[ClaimCheck] = []
    sentences = [s.strip() for s in draft.split(".") if s.strip()]
    evidence_text = " ".join(f"{e.title} {e.excerpt} {' '.join(e.skills)}".lower() for e in evidence)
    for sentence in sentences:
        lowered = sentence.lower()
        if any(token in lowered for token in ("guarantee", "best", "years of experience", "million")):
            checks.append(ClaimCheck(claim=sentence, status="unsupported"))
        elif any(skill.lower() in lowered for item in evidence for skill in item.skills) and any(word in evidence_text for word in lowered.split() if len(word) > 5):
            ids = [item.id for item in evidence if any(skill.lower() in lowered for skill in item.skills)]
            checks.append(ClaimCheck(claim=sentence, status="supported", evidence_ids=ids))
        else:
            checks.append(ClaimCheck(claim=sentence, status="partly_supported"))
    return checks

