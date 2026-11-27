# GigBid demo briefing

## One-sentence description

GigBid is a **human-approved freelance proposal copilot**: it assesses a job, retrieves portfolio evidence, drafts a grounded proposal, checks each claim, and stops for a reviewer before any marketplace action.

## The three-minute walkthrough

1. Open <https://gigbid-api-pn5q.onrender.com>. Say that the page is the React reviewer dashboard served with a FastAPI backend.
2. Select **Build a small inventory forecasting API** and click **Run safe analysis**. Explain that this is a safe analysis only, not a live Upwork submission.
3. Point to the decision trail. Scout first structures the job; **Analyst**, **Risk**, and **Fit** run as separate checks; then the workflow decides whether to bid, calculates a price, writes a draft, verifies claims, and checks compliance.
4. Show the evidence cards and proposal studio. Explain that the draft is editable and every claim is marked supported, partly supported, or unsupported. The graph stops at a human approval gate.
5. If asked to demonstrate approval, sign in as the reviewer and choose **Approve dry-run draft**. This records an idempotent dry-run preview; it does not submit a real proposal or spend Connects.
6. Select **Urgent dashboard help - contact me on Telegram** and run the analysis. Explain that it is skipped because it asks for off-platform contact and free work. Job text is handled as untrusted input.
7. Open <https://gigbid-portfolio-mcp.onrender.com>. Explain that this is the browser landing page for the deployed, read-only Portfolio MCP server. MCP clients use the `/mcp` route; a normal browser must not be used to test that protocol route.

## Concepts to explain

| Concept | Simple explanation |
|---|---|
| React | The frontend dashboard the reviewer uses. |
| FastAPI | The Python backend that exposes the API and serves the deployed app. |
| LangGraph | The orchestration framework for the executable workflow. It represents the steps and state transitions as a graph instead of one large prompt. |
| Parallel checks | After Scout, Analyst, Risk, and Fit independently examine the job before the workflow makes a decision. |
| RAG | Retrieval-augmented generation: retrieve relevant portfolio evidence first, then use that evidence when producing the draft. |
| Claim verification | The proposal is broken into claims and labelled according to supporting portfolio evidence, so it does not invent experience. |
| MCP | Model Context Protocol: a standard way for an AI host to discover and call tools. The Portfolio MCP exposes `search_evidence`, `get_case_study`, and `list_skills`. |
| Human-in-the-loop | The system can analyse and draft, but a human must approve before the marketplace adapter creates even a dry-run preview. |
| Idempotency key | A unique request key that prevents the same approval from being processed twice after a retry. |

## Honest boundaries

- The app is deployed and the graph, UI, API, Portfolio MCP service, claim checks, and safety checks are working.
- The current jobs and portfolio are synthetic demo data. The redacted public job-posting corpus is documented separately.
- The marketplace adapter is in **demo mode**. It does not scrape Upwork, automate a browser, send proposals, or spend Connects.
- The checked-in evaluation is a reproducible three-job synthetic smoke test. Its metrics must not be described as live marketplace performance or a GigSim result.
- The RAG variants are deterministic retrieval baselines, not claims of a trained embedding model or production-quality ranking experiment.

## Likely questions and concise answers

**Why LangGraph rather than a single prompt?**  It makes the steps, state, parallel checks, and approval interruption explicit and testable. A reviewer can see why the system reached a decision.

**How do you prevent hallucinated proposal claims?**  GigBid retrieves portfolio evidence, links claims to that evidence, and labels unsupported or partially supported claims before approval.

**Why is the Telegram job skipped?**  It contains risk signals: off-platform contact, free work, and instructions that conflict with platform rules. The risk checker sees job text as untrusted input.

**What does the Portfolio MCP add?**  It separates reusable portfolio retrieval tools from the main application. A compatible MCP client can search evidence or fetch a case study without directly coupling to the web app database.

**Why did the MCP URL show an error in a browser?**  `/mcp` is a Streamable HTTP protocol endpoint, not a webpage; it requires MCP event-stream headers. The server's root URL is the human-readable landing page.

**Did the app submit a proposal to Upwork?**  No. This deployment is intentionally dry-run only. Human approval produces a preview and idempotency record, not a live marketplace write.

**How was it evaluated?**  The included evaluation is a deterministic, three-job synthetic smoke test for decision, retrieval, claim, latency, and cost plumbing. It is not a live-marketplace or course-simulator result.

**What would you add for production?**  Official OAuth/MCP marketplace integration, PostgreSQL-backed checkpoints, tenant isolation, rate limits, audit retention, real portfolio consent/provenance, and course-scale GigSim evaluation.

## Avoid saying

- Do not call the synthetic evaluation a real-world accuracy result.
- Do not say it has live Upwork access, sends proposals, or spends Connects.
- Do not say a browser opening `/mcp` is an MCP test; use the landing page or an MCP client.
- Follow the repository's AI-use disclosure and describe the work accurately if asked.
