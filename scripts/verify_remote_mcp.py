"""Perform a standards-level Streamable HTTP MCP initialization check.

Usage:
    python scripts/verify_remote_mcp.py https://gigbid-portfolio-mcp.onrender.com/mcp
"""
from __future__ import annotations

import argparse
import json

import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("endpoint", nargs="?", default="https://gigbid-portfolio-mcp.onrender.com/mcp")
    args = parser.parse_args()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "gigbid-verifier", "version": "0.1"},
        },
    }
    headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    with httpx.Client(timeout=30) as client:
        response = client.post(args.endpoint, headers=headers, json=payload)
    response.raise_for_status()
    if "mcp-session-id" not in response.headers:
        raise RuntimeError("MCP endpoint did not return a session ID")
    print(json.dumps({"endpoint": args.endpoint, "status": response.status_code, "session_created": True, "response": response.text}, indent=2))


if __name__ == "__main__":
    main()
