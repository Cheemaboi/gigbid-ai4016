"""Portfolio MCP server. Run with: python -m mcp_servers.portfolio.server"""
from __future__ import annotations
import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import HTMLResponse, JSONResponse

ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO = json.loads((ROOT / "data/processed/demo_portfolio.json").read_text(encoding="utf-8"))
public_host = os.getenv("PUBLIC_HOST", "").strip()
allowed_hosts = ["localhost:*", "127.0.0.1:*", "[::1]:*"]
if public_host:
    allowed_hosts.append(public_host)
else:
    # This server exposes synthetic, read-only course data. Set PUBLIC_HOST in production
    # to replace this convenience wildcard with the precise deployed hostname.
    allowed_hosts.append("*.onrender.com")
mcp = FastMCP(
    "GigBid Portfolio",
    instructions="Read-only evidence server for a freelancer portfolio.",
    host="0.0.0.0" if os.getenv("MCP_TRANSPORT") == "streamable-http" else "127.0.0.1",
    port=int(os.getenv("PORT", "8000")),
    transport_security=TransportSecuritySettings(allowed_hosts=allowed_hosts),
)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Unauthenticated liveness endpoint for the hosting platform."""
    return JSONResponse({"status": "ok", "server": "GigBid Portfolio", "transport": os.getenv("MCP_TRANSPORT", "stdio")})


@mcp.custom_route("/", methods=["GET"])
async def landing_page(request):
    """Human-readable entry point; the MCP protocol itself lives at /mcp."""
    return HTMLResponse(
        """<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>GigBid Portfolio MCP</title><style>body{font-family:system-ui,sans-serif;max-width:720px;margin:10vh auto;padding:0 24px;line-height:1.55;color:#172033}code{background:#edf2f7;padding:2px 5px;border-radius:4px}a{color:#1d4ed8}</style></head><body><h1>GigBid Portfolio MCP</h1><p>This is a public, read-only Model Context Protocol server used by GigBid to retrieve portfolio evidence.</p><p><strong>For MCP clients:</strong> connect to <code>/mcp</code> using Streamable HTTP. Opening that protocol URL directly in a browser is not a failure: browsers do not send the required MCP <code>Accept</code> headers.</p><h2>Available tools</h2><ul><li><code>search_evidence</code> — retrieve relevant portfolio evidence</li><li><code>get_case_study</code> — retrieve a case study by ID</li><li><code>list_skills</code> — list portfolio skills</li></ul><p><a href=\"/health\">Health check</a> · <a href=\"https://github.com/Cheemaboi/gigbid-ai4016/blob/master/docs/PORTFOLIO_MCP.md\">Technical write-up</a></p></body></html>"""
    )


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
    mcp.run(transport=os.getenv("MCP_TRANSPORT", "stdio"))

