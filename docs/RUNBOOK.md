# Runbook

## Local development

1. Install Python and web dependencies using the README commands.
2. Start the API on port 8000 and the web client on port 5173.
3. Verify `/health` returns `{"status":"ok","mode":"demo"}`.
4. Run `python -m pytest -q` before changing a graph or tool contract.

## Demo recovery

If the UI says the marketplace is unavailable, check the API terminal, restart `python -m uvicorn apps.api.main:app --reload --port 8000`, then use **Refresh jobs**. The demo data is read-only JSON; restarting clears in-memory proposal drafts by design.

## Safe deployment checklist

- Set a non-demo reviewer password in the host secret manager.
- Set the web application's `VITE_API_URL` to the deployed API URL.
- Restrict CORS to the deployed web origin.
- Use HTTPS and a managed database before storing any real user data.
- Keep all OAuth tokens encrypted and out of logs.
- Configure conservative scheduled polling only after validating official Upwork MCP limits.
- Test the approval path and idempotent retry after a process restart.

## Full-stack deployment with Render and GitHub Pages

1. In Render, create a Blueprint from the public repository. This repository's `render.yaml` creates both the `gigbid-api` FastAPI service and the `gigbid-portfolio-mcp` service.
2. Copy the FastAPI URL shown by Render, for example `https://gigbid-api.onrender.com`.
3. In GitHub, open **Settings > Secrets and variables > Actions**, create a repository secret named `VITE_API_URL`, and paste that API URL. Do not add a trailing slash.
4. Run the **Publish browser demo** workflow again, or push a harmless documentation change. The Pages build receives `VITE_API_URL` and will call the deployed API instead of its browser-only fallback.
5. Open `https://YOUR-API.onrender.com/health` and then the public Pages URL. The status message should change from browser-only demo to demo marketplace available.

## Incident response

Disable live marketplace writes first. Preserve masked audit data and the idempotency key. Do not retry a proposal submission until its upstream status is known. If a prompt-injection pattern appears, add a redacted test case and review the risk rule before re-enabling the queue.

