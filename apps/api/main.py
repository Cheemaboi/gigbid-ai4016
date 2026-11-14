from __future__ import annotations
import json
import os
import base64
import hashlib
import hmac
import time
from pathlib import Path
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent.graphs.bid_graph import analyze, run_bid_graph as execute_bid_graph
from agent.marketplace_port import DemoMarketplaceAdapter

ROOT = Path(__file__).resolve().parents[2]
JOBS = json.loads((ROOT / "data/processed/demo_jobs.json").read_text(encoding="utf-8"))
PORTFOLIO = json.loads((ROOT / "data/processed/demo_portfolio.json").read_text(encoding="utf-8"))
REAL_JOB_SAMPLE = json.loads((ROOT / "data/processed/upwork_jobs_2024_sample.json").read_text(encoding="utf-8"))
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


class LoginRequest(BaseModel):
    username: str
    password: str


REVIEWER_USERNAME = os.getenv("REVIEWER_USERNAME", "reviewer")
# The local value exists solely for offline tests. Render overrides it with a generated secret.
REVIEWER_PASSWORD = os.getenv("REVIEWER_PASSWORD", "local-demo-only")


def _issue_token(username: str) -> str:
    """Issue a short-lived HMAC token without persisting a password or session."""
    payload = f"{username}:{int(time.time()) + 60 * 60 * 4}"
    signature = hmac.new(REVIEWER_PASSWORD.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}:{signature}".encode()).decode()


def require_reviewer(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Reviewer sign-in required")
    try:
        raw = base64.urlsafe_b64decode(authorization.removeprefix("Bearer ").encode()).decode()
        username, expiry, signature = raw.rsplit(":", 2)
        payload = f"{username}:{expiry}"
        expected = hmac.new(REVIEWER_PASSWORD.encode(), payload.encode(), hashlib.sha256).hexdigest()
        valid = hmac.compare_digest(signature, expected) and username == REVIEWER_USERNAME and int(expiry) >= time.time()
    except (ValueError, UnicodeDecodeError):
        valid = False
    if not valid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Reviewer session is invalid or expired")
    return REVIEWER_USERNAME


@app.post("/auth/login")
def reviewer_login(request: LoginRequest):
    if not (hmac.compare_digest(request.username, REVIEWER_USERNAME) and hmac.compare_digest(request.password, REVIEWER_PASSWORD)):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid reviewer credentials")
    return {"access_token": _issue_token(REVIEWER_USERNAME), "token_type": "bearer", "expires_in_seconds": 14400}


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


@app.get("/research/upwork-2024")
def research_job_sample(limit: int = 20):
    """Return attributed public-dataset records without presenting them as a live feed."""
    limit = max(1, min(limit, 100))
    return {"metadata": REAL_JOB_SAMPLE["metadata"], "records": REAL_JOB_SAMPLE["records"][:limit]}

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
    state = execute_bid_graph(job, PORTFOLIO)
    result = {key: state[key] for key in ("job_spec", "risk", "fit", "price", "decision")}
    proposal = state.get("proposal")
    payload = {"analysis": {key: value.model_dump() for key, value in result.items()}, "events": state["events"]}
    if proposal:
        DRAFTS[proposal.id] = proposal.model_dump()
        payload.update({"draft": proposal.model_dump(), "events": payload["events"] + ["interrupt: human_approval"]})
    AUDIT.append({"event": "graph_run", "job_id": job_id, "result": result["decision"].action})
    return payload

@app.get("/proposals/{draft_id}")
def get_proposal(draft_id: str):
    if draft_id not in DRAFTS: raise HTTPException(404, "Proposal not found")
    return DRAFTS[draft_id]

@app.post("/proposals/{draft_id}/approve")
def approve_proposal(draft_id: str, request: ApprovalRequest, reviewer: str = Depends(require_reviewer)):
    proposal = DRAFTS.get(draft_id)
    if not proposal: raise HTTPException(404, "Proposal not found")
    if proposal["status"] != "awaiting_approval": raise HTTPException(409, "Proposal is not awaiting approval")
    if request.edited_body: proposal["body"] = request.edited_body
    job = MARKETPLACE.get_job(proposal["job_id"])
    preview = MARKETPLACE.create_proposal_draft({"job_id": job["id"], "body": proposal["body"], "connects_cost": job["connects_cost"]}, request.idempotency_key, dry_run=True)
    proposal["status"] = "approved"
    proposal["dry_run_preview"] = preview
    AUDIT.append({"event": "approval", "draft_id": draft_id, "idempotency_key": request.idempotency_key, "reviewer": reviewer})
    return proposal

@app.post("/proposals/{draft_id}/reject")
def reject_proposal(draft_id: str, request: RejectionRequest, reviewer: str = Depends(require_reviewer)):
    proposal = DRAFTS.get(draft_id)
    if not proposal: raise HTTPException(404, "Proposal not found")
    proposal["status"] = "rejected"; proposal["rejection_reason"] = request.reason
    AUDIT.append({"event": "rejection", "draft_id": draft_id, "reason": request.reason, "reviewer": reviewer})
    return proposal

@app.get("/analytics")
def analytics():
    return {"jobs_scanned": len(JOBS), "drafts": len(DRAFTS), "approved": sum(d["status"] == "approved" for d in DRAFTS.values()),
            "p95_latency_seconds": 0.18, "cost_per_proposal_usd": 0.0, "note": "Offline deterministic demo metrics, not live marketplace outcomes."}


# The Render production image builds the React application into this directory.
# Mounting it last keeps every documented API route above available.
static_dir = ROOT / "apps" / "web" / "dist"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="web")

