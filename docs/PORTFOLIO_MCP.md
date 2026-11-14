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

Connect it through an MCP host using standard I/O transport. Before publishing, host it behind authenticated Streamable HTTP, publish its endpoint in the README, and verify it with MCP Inspector. This repository does not claim a public server has already been hosted.

