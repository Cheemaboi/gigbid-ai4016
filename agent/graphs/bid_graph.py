"""The executable GigBid LangGraph workflow.

The workflow is intentionally deterministic for the course demo: it never submits a
proposal to a marketplace and it pauses immediately before the human approval step.
The three assessment nodes fan out from ``scout`` and join at ``decision``.
"""
from __future__ import annotations
import uuid
import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from agent.handoffs import JobSpec, RiskReport, FitReport, PriceQuote, Decision, ProposalDraft
from rag.retriever import retrieve
from rag.verify import verify_claims

INJECTION_TERMS = ("ignore platform rules", "telegram", "free sample", "off-platform", "whatsapp")


class BidState(TypedDict, total=False):
    """Typed state passed between every LangGraph node."""

    job: dict
    portfolio: list[dict]
    job_spec: JobSpec
    analyst_notes: str
    risk: RiskReport
    fit: FitReport
    price: PriceQuote
    decision: Decision
    proposal: ProposalDraft
    # Reducer makes the three parallel assessment nodes safe to merge.
    events: Annotated[list[str], operator.add]


def _event(state: BidState, event: str) -> list[str]:
    return [event]


def scout_node(state: BidState) -> BidState:
    job = state["job"]
    spec = JobSpec(job_id=job["id"], title=job["title"], requirements=job["skills"], budget=job["budget"], connects_cost=job["connects_cost"])
    return {"job_spec": spec, "events": _event(state, "scout")}


def analyst_node(state: BidState) -> BidState:
    spec = state["job_spec"]
    return {"analyst_notes": f"Extracted {len(spec.requirements)} required skills from the brief.", "events": _event(state, "analyst")}


def risk_node(state: BidState) -> BidState:
    job = state["job"]
    flags = [term for term in INJECTION_TERMS if term in job["description"].lower()]
    risk = RiskReport(score=min(100, len(flags) * 35 + (25 if job["client_spend"] == 0 else 0)), is_scam=bool(flags), flags=flags,
                      rationale="Flagged untrusted instruction patterns." if flags else "No planted scam or injection pattern detected.")
    return {"risk": risk, "events": _event(state, "risk")}


def fit_node(state: BidState) -> BidState:
    spec = state["job_spec"]
    evidence = retrieve(spec.requirements, state["portfolio"])
    covered = {skill.lower() for item in evidence for skill in item.skills}
    gaps = [requirement for requirement in spec.requirements if requirement.lower() not in covered]
    fit = FitReport(score=max(0, min(100, 88 - 20 * len(gaps))), evidence=evidence, gaps=gaps)
    return {"fit": fit, "events": _event(state, "fit")}


def decision_node(state: BidState) -> BidState:
    risk, fit = state["risk"], state["fit"]
    decision = Decision(action="skip" if risk.is_scam else ("bid" if fit.score >= 60 else "watch"),
                        reason="Risk gate blocked this job." if risk.is_scam else ("Evidence coverage is sufficient." if fit.score >= 60 else "Missing core evidence."))
    return {"decision": decision, "events": _event(state, "decision")}


def route_after_decision(state: BidState) -> Literal["pricing", "end"]:
    return "pricing" if state["decision"].action == "bid" else "end"


def pricing_node(state: BidState) -> BidState:
    job, fit, risk = state["job"], state["fit"], state["risk"]
    bid = round(max(120, min(job["budget"], job["budget"] * (0.82 if fit.score > 70 else 0.7))), 2)
    price = PriceQuote(recommended_bid=bid, connects_worth_spending=not risk.is_scam and fit.score >= 60,
                       rationale=f"Within the ${job['budget']:.0f} client budget and based on fit score {fit.score}.")
    return {"price": price, "events": _event(state, "pricing")}


def writer_node(state: BidState) -> BidState:
    job, evidence, price = state["job"], state["fit"].evidence, state["price"]
    primary = evidence[0]
    body = (f"Hello {job['client']},\n\nYour {job['title'].lower()} caught my attention because it needs "
            f"{', '.join(job['skills'][:2])}. I can start by confirming the data flow and agreeing on a small, testable first milestone. "
            f"A relevant example is {primary.title}, where I worked with {', '.join(primary.skills[:2])}. "
            f"For this scope, I would propose ${price.recommended_bid:.0f} and provide concise handover notes.\n\nBest regards")
    proposal = ProposalDraft(id=f"draft-{uuid.uuid4().hex[:8]}", job_id=job["id"], body=body, price=price.recommended_bid,
                             claims=[], status="drafting")
    return {"proposal": proposal, "events": _event(state, "writer")}


def verifier_node(state: BidState) -> BidState:
    proposal = state["proposal"].model_copy(deep=True)
    proposal.claims = verify_claims(proposal.body, state["fit"].evidence)
    return {"proposal": proposal, "events": _event(state, "verifier")}


def compliance_node(state: BidState) -> BidState:
    proposal = state["proposal"].model_copy(deep=True)
    unsupported = [claim.claim for claim in proposal.claims if claim.status == "unsupported"]
    proposal.compliance_notes = ["Blocked unsupported claim: " + item for item in unsupported]
    proposal.status = "awaiting_approval"
    return {"proposal": proposal, "events": _event(state, "compliance")}


def human_approval_node(state: BidState) -> BidState:
    """Deliberately never reached by normal runs: LangGraph interrupts before it."""
    return {"events": _event(state, "human_approval")}


def build_bid_graph():
    graph = StateGraph(BidState)
    graph.add_node("scout", scout_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("risk", risk_node)
    graph.add_node("fit", fit_node)
    graph.add_node("decision", decision_node)
    graph.add_node("pricing", pricing_node)
    graph.add_node("writer", writer_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("compliance", compliance_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_edge(START, "scout")
    graph.add_edge("scout", "analyst")
    graph.add_edge("scout", "risk")
    graph.add_edge("scout", "fit")
    graph.add_edge("analyst", "decision")
    graph.add_edge("risk", "decision")
    graph.add_edge("fit", "decision")
    graph.add_conditional_edges("decision", route_after_decision, {"pricing": "pricing", "end": END})
    graph.add_edge("pricing", "writer")
    graph.add_edge("writer", "verifier")
    graph.add_edge("verifier", "compliance")
    graph.add_edge("compliance", "human_approval")
    graph.add_edge("human_approval", END)
    return graph.compile(interrupt_before=["human_approval"])


def run_bid_graph(job: dict, portfolio: list[dict]) -> BidState:
    """Run through compliance and pause at the explicit human approval boundary."""
    return build_bid_graph().invoke({"job": job, "portfolio": portfolio, "events": []})


def analyze(job: dict, portfolio: list[dict]) -> dict:
    state = run_bid_graph(job, portfolio)
    return {key: state[key] for key in ("job_spec", "risk", "fit", "price", "decision")}


def draft(job: dict, portfolio: list[dict]) -> tuple[dict, ProposalDraft | None]:
    state = run_bid_graph(job, portfolio)
    result = {key: state[key] for key in ("job_spec", "risk", "fit", "price", "decision")}
    if result["decision"].action != "bid":
        return result, None
    return result, state["proposal"]

