"""Portfolio MCP server. Run with: python -m mcp_servers.portfolio.server"""
from __future__ import annotations
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO = json.loads((ROOT / "data/processed/demo_portfolio.json").read_text(encoding="utf-8"))
mcp = FastMCP("GigBid Portfolio", instructions="Read-only evidence server for a freelancer portfolio.")


@mcp.tool()
def search_evidence(requirement: str, k: int = 5, outcome: str | None = None) -> list[dict]:
    """Find portfolio evidence for a job requirement. Read-only."""
    terms = set(requirement.lower().split())
    items = [item for item in PORTFOLIO if not outcome or item["outcome"] == outcome]
    ranked = sorted(items, key=lambda item: len(terms & set((item["title"] + " " + item["content"] + " " + " ".join(item["skills"])).lower().split())), reverse=True)
    return ranked[:max(1, min(k, 10))]


@mcp.tool()
def get_case_study(id: str) -> dict:
    """Load one complete portfolio item by stable id. Read-only."""
    return next(item for item in PORTFOLIO if item["id"] == id)


@mcp.tool()
def list_skills() -> list[str]:
    """List portfolio skills. Read-only."""
    return sorted({skill for item in PORTFOLIO for skill in item["skills"]})


@mcp.resource("portfolio://case/{case_id}")
def case_resource(case_id: str) -> str:
    return json.dumps(get_case_study(case_id), indent=2)


@mcp.prompt()
def answer_from_portfolio(question: str) -> str:
    return f"Answer this question only with evidence returned by search_evidence. If evidence is missing, say so plainly. Question: {question}"


if __name__ == "__main__":
    mcp.run()

