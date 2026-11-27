# Portfolio MCP technical write-up

The Portfolio MCP server is a small, read-only server intended to make a freelancer's evidence portable between compatible MCP hosts. Its implementation is at [`mcp_servers/portfolio/server.py`](../mcp_servers/portfolio/server.py).

## Tools

- `search_evidence(requirement, k, outcome)` ranks evidence by requirement overlap.
- `get_case_study(id)` returns a full item with provenance fields.
- `list_skills()` provides a compact discovery view.

It also exposes `portfolio://case/{case_id}` resources and an `answer_from_portfolio` prompt template. The source data is synthetic in this repository. A production version must authenticate each portfolio owner, store source provenance, and ensure that an imported repository or CV has the owner's consent.

## Run locally

```bash
python -m mcp_servers.portfolio.server
```

## Published deployment

The public browser landing page is <https://gigbid-portfolio-mcp.onrender.com>. The Streamable HTTP endpoint for MCP clients is <https://gigbid-portfolio-mcp.onrender.com/mcp>. `MCP_TRANSPORT=streamable-http` and the Render hostname are configured in `render.yaml`. A direct browser visit to `/mcp` returns an HTTP 406 because a browser does not negotiate the MCP event-stream media type; use the landing page or an MCP client instead.

Verify a real MCP initialization (rather than a browser GET) with:

```bash
python scripts/verify_remote_mcp.py
```

The deployment runs the same read-only tools; no browser scraping, secret, or live marketplace data is involved. In a real portfolio deployment, replace the synthetic corpus and add user authentication and tenant isolation.

