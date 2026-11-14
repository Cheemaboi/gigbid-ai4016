"""A hand-written, inspectable approximation of the bid StateGraph.

The production design maps these deterministic nodes to LangGraph nodes. Keeping the
node contracts pure makes unit tests and an offline demo reliable.
"""
from __future__ import annotations
import uuid
from agent.handoffs import JobSpec, RiskReport, FitReport, PriceQuote, Decision, ProposalDraft
from rag.retriever import retrieve
from rag.verify import verify_claims

INJECTION_TERMS = ("ignore platform rules", "telegram", "free sample", "off-platform", "whatsapp")


def analyze(job: dict, portfolio: list[dict]) -> dict:
    spec = JobSpec(job_id=job["id"], title=job["title"], requirements=job["skills"], budget=job["budget"], connects_cost=job["connects_cost"])
    text = job["description"].lower()
    flags = [term for term in INJECTION_TERMS if term in text]
    risk = RiskReport(score=min(100, len(flags) * 35 + (25 if job["client_spend"] == 0 else 0)), is_scam=bool(flags), flags=flags,
                      rationale="Flagged untrusted instruction patterns." if flags else "No planted scam or injection pattern detected.")
    evidence = retrieve(spec.requirements, portfolio)
    covered = {skill.lower() for item in evidence for skill in item.skills}
    gaps = [requirement for requirement in spec.requirements if requirement.lower() not in covered]
    fit = FitReport(score=max(0, min(100, 88 - 20 * len(gaps))), evidence=evidence, gaps=gaps)
    bid = round(max(120, min(job["budget"], job["budget"] * (0.82 if fit.score > 70 else 0.7))), 2)
    price = PriceQuote(recommended_bid=bid, connects_worth_spending=not risk.is_scam and fit.score >= 60,
                       rationale=f"Within the ${job['budget']:.0f} client budget and based on fit score {fit.score}.")
    decision = Decision(action="skip" if risk.is_scam else ("bid" if fit.score >= 60 else "watch"),
                        reason="Risk gate blocked this job." if risk.is_scam else ("Evidence coverage is sufficient." if fit.score >= 60 else "Missing core evidence."))
    return {"job_spec": spec, "risk": risk, "fit": fit, "price": price, "decision": decision}


def draft(job: dict, portfolio: list[dict]) -> tuple[dict, ProposalDraft | None]:
    result = analyze(job, portfolio)
    if result["decision"].action != "bid":
        return result, None
    evidence = result["fit"].evidence
    primary = evidence[0]
    body = (f"Hello {job['client']},\n\nYour {job['title'].lower()} caught my attention because it needs "
            f"{', '.join(job['skills'][:2])}. I can start by confirming the data flow and agreeing on a small, testable first milestone. "
            f"A relevant example is {primary.title}, where I worked with {', '.join(primary.skills[:2])}. "
            f"For this scope, I would propose ${result['price'].recommended_bid:.0f} and provide concise handover notes.\n\nBest regards")
    claims = verify_claims(body, evidence)
    draft_obj = ProposalDraft(id=f"draft-{uuid.uuid4().hex[:8]}", job_id=job["id"], body=body, price=result["price"].recommended_bid,
                              claims=claims, status="awaiting_approval")
    unsupported = [claim.claim for claim in claims if claim.status == "unsupported"]
    if unsupported:
        draft_obj.compliance_notes = ["Blocked unsupported claim: " + item for item in unsupported]
    return result, draft_obj

