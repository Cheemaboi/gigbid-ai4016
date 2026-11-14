# Tool inventory and trust boundaries

| Tool | Server | Access | Important constraints | Auth |
|---|---|---|---|---|
| `search_evidence` | Portfolio | Read | Returns provenance and outcome; no portfolio edits | Local demo / future user token |
| `get_case_study` | Portfolio | Read | Stable id only | Local demo / future user token |
| `list_skills` | Portfolio | Read | No private fields | Local demo / future user token |
| `search_jobs` | Marketplace | Read | Demo data only; live mode must use official Upwork MCP | Bearer token in production |
| `get_job` | Marketplace | Read | Scoped to a tenant in production | Bearer token in production |
| `get_connects_balance` | Marketplace | Read | Rate limited in production | Bearer token in production |
| `create_proposal_draft` | Marketplace | Write draft | Requires idempotency key; preview only until UI approval | Bearer token in production |
| `list_free_slots` | Workspace | Read | Local mock records one safe slot | Local demo / OAuth in production |
| `create_email_draft` | Workspace | Write draft | Never sends email | Local demo / OAuth in production |

The Portfolio server is independently usable through an MCP host. The project trusts the official Upwork MCP server for live platform access because it exposes OAuth-protected, documented platform actions. A GitHub MCP server would be used for optional repository ingestion after a user grants access; no browser scraping or cookie automation is used.

