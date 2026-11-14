from __future__ import annotations
import json
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.graphs.bid_graph import analyze, draft
from agent.marketplace_port import DemoMarketplaceAdapter

ROOT = Path(__file__).resolve().parents[2]
JOBS = json.loads((ROOT / "data/processed/demo_jobs.json").read_text(encoding="utf-8"))
PORTFOLIO = json.loads((ROOT / "data/processed/demo_portfolio.json").read_text(encoding="utf-8"))
MARKETPLACE = DemoMarketplaceAdapter(JOBS)
DRAFTS: dict[str, dict] = {}
AUDIT: list[dict] = []

app = FastAPI(title="GigBid API", version="0.1.0")
origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,https://cheemaboi.github.io").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class ApprovalRequest(BaseModel):
    edited_body: str | None = None
    idempotency_key: str


class RejectionRequest(BaseModel):
    reason: str


@app.get("/health")
def health(): return {"status": "ok", "mode": "demo", "marketplace": "available"}

@app.get("/jobs")
def list_jobs():
    result = []
    for job in JOBS:
        analysis = analyze(job, PORTFOLIO)
        result.append({**job, "fit_score": analysis["fit"].score, "risk_score": analysis["risk"].score,
                       "recommendation": analysis["decision"].action, "recommended_bid": analysis["price"].recommended_bid})
    return result

@app.get("/jobs/{job_id}")
def job_detail(job_id: str):
    try: job = MARKETPLACE.get_job(job_id)
    except KeyError: raise HTTPException(404, "Job not found")
    result = analyze(job, PORTFOLIO)
    return {"job": job, "analysis": {key: value.model_dump() for key, value in result.items()}}

@app.post("/jobs/{job_id}/run")
def run_bid_graph(job_id: str):
    try: job = MARKETPLACE.get_job(job_id)
    except KeyError: raise HTTPException(404, "Job not found")
    result, proposal = draft(job, PORTFOLIO)
    payload = {"analysis": {key: value.model_dump() for key, value in result.items()}, "events": ["scout", "analyst+risk+fit (parallel)", "decision"]}
    if proposal:
        DRAFTS[proposal.id] = proposal.model_dump()
        payload.update({"draft": proposal.model_dump(), "events": payload["events"] + ["pricing", "writer", "verifier", "compliance", "interrupt: approval"]})
    AUDIT.append({"event": "graph_run", "job_id": job_id, "result": result["decision"].action})
    return payload

@app.get("/proposals/{draft_id}")
def get_proposal(draft_id: str):
    if draft_id not in DRAFTS: raise HTTPException(404, "Proposal not found")
    return DRAFTS[draft_id]

@app.post("/proposals/{draft_id}/approve")
def approve_proposal(draft_id: str, request: ApprovalRequest):
    proposal = DRAFTS.get(draft_id)
    if not proposal: raise HTTPException(404, "Proposal not found")
    if proposal["status"] != "awaiting_approval": raise HTTPException(409, "Proposal is not awaiting approval")
    if request.edited_body: proposal["body"] = request.edited_body
    job = MARKETPLACE.get_job(proposal["job_id"])
    preview = MARKETPLACE.create_proposal_draft({"job_id": job["id"], "body": proposal["body"], "connects_cost": job["connects_cost"]}, request.idempotency_key, dry_run=True)
    proposal["status"] = "approved"
    proposal["dry_run_preview"] = preview
    AUDIT.append({"event": "approval", "draft_id": draft_id, "idempotency_key": request.idempotency_key})
    return proposal

@app.post("/proposals/{draft_id}/reject")
def reject_proposal(draft_id: str, request: RejectionRequest):
    proposal = DRAFTS.get(draft_id)
    if not proposal: raise HTTPException(404, "Proposal not found")
    proposal["status"] = "rejected"; proposal["rejection_reason"] = request.reason
    AUDIT.append({"event": "rejection", "draft_id": draft_id, "reason": request.reason})
    return proposal

@app.get("/analytics")
def analytics():
    return {"jobs_scanned": len(JOBS), "drafts": len(DRAFTS), "approved": sum(d["status"] == "approved" for d in DRAFTS.values()),
            "p95_latency_seconds": 0.18, "cost_per_proposal_usd": 0.0, "note": "Offline deterministic demo metrics, not live marketplace outcomes."}

