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

## Incident response

Disable live marketplace writes first. Preserve masked audit data and the idempotency key. Do not retry a proposal submission until its upstream status is known. If a prompt-injection pattern appears, add a redacted test case and review the risk rule before re-enabling the queue.

