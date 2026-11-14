"""Demo Marketplace MCP service with explicit dry-run writes and idempotency."""
from __future__ import annotations
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[2]
JOBS = json.loads((ROOT / "data/processed/demo_jobs.json").read_text(encoding="utf-8"))
mcp = FastMCP("GigBid Marketplace", instructions="Demo only. Every write is a draft and needs human approval upstream.")
_writes: dict[str, dict] = {}


@mcp.tool()
def search_jobs(query: str = "") -> list[dict]:
    """Search locally seeded jobs. Read-only."""
    query = query.lower()
    return [job for job in JOBS if query in (job["title"] + job["description"]).lower()]


@mcp.tool()
def get_job(job_id: str) -> dict:
    """Get a job and basic client history. Read-only."""
    return next(job for job in JOBS if job["id"] == job_id)


@mcp.tool()
def get_connects_balance() -> dict:
    """Return demo balance. Read-only."""
    return {"available": 40, "weekly_budget": 40}


@mcp.tool()
def create_proposal_draft(job_id: str, body: str, price: float, idempotency_key: str, dry_run: bool = True) -> dict:
    """Preview a proposal draft. Does not send a proposal. Requires an idempotency key."""
    if idempotency_key not in _writes:
        job = get_job(job_id)
        _writes[idempotency_key] = {"id": f"preview-{idempotency_key[:8]}", "status": "draft_preview", "dry_run": dry_run, "connects_cost": job["connects_cost"], "body": body, "price": price}
    return _writes[idempotency_key]


if __name__ == "__main__":
    mcp.run()

