from __future__ import annotations
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("GigBid Workspace", instructions="Local mock for calendar availability and email drafting.")

@mcp.tool()
def list_free_slots(days: int = 7) -> list[dict]:
    """Read-only local availability."""
    return [{"start": "2026-11-17T14:00:00+05:00", "end": "2026-11-17T14:30:00+05:00", "timezone": "Asia/Karachi"}]

@mcp.tool()
def create_email_draft(to: str, subject: str, body: str) -> dict:
    """Create a local email draft only; no message is sent."""
    return {"status": "draft", "to": to, "subject": subject, "body": body}

if __name__ == "__main__":
    mcp.run()

