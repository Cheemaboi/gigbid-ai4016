import json
from pathlib import Path
from agent.graphs.bid_graph import draft

ROOT = Path(__file__).resolve().parents[2]
JOBS = json.loads((ROOT / "data/processed/demo_jobs.json").read_text())
PORTFOLIO = json.loads((ROOT / "data/processed/demo_portfolio.json").read_text())

def test_safe_job_stops_for_human_approval():
    result, proposal = draft(JOBS[0], PORTFOLIO)
    assert result["decision"].action == "bid"
    assert proposal and proposal.status == "awaiting_approval"

def test_injection_job_is_skipped():
    result, proposal = draft(JOBS[1], PORTFOLIO)
    assert result["risk"].is_scam is True
    assert result["decision"].action == "skip"
    assert proposal is None

