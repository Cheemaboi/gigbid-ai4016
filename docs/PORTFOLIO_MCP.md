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

## Publish it on Render

The repository now includes `render.yaml` and `infra/docker/portfolio-mcp.Dockerfile`, so this needs only a Render account linked to GitHub, not an API key.

1. Sign in at [Render](https://dashboard.render.com/) using GitHub and authorise access to `Cheemaboi/gigbid-ai4016`.
2. Choose **New** then **Blueprint**, select the repository, and accept the `gigbid-portfolio-mcp` service proposed by `render.yaml`.
3. In the service Environment page, set `PUBLIC_HOST` to the hostname Render assigns, for example `gigbid-portfolio-mcp.onrender.com`, then deploy once more.
4. The published endpoint is `https://YOUR-HOST.onrender.com/mcp`. Use that exact URL in MCP Inspector and in the private submission comment.

`MCP_TRANSPORT=streamable-http` is configured by the Blueprint. It runs the same read-only tools remotely; no browser scraping, secret, or live marketplace data is involved. In a real portfolio deployment, replace the synthetic corpus, add user authentication, and set `PUBLIC_HOST` precisely instead of relying on the safe course-demo fallback.

