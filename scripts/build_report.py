"""Build the submitted R&D report from the committed research corpus and pilot results."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "GigBid_RD_Report.pdf"
navy, blue, pale, ink = colors.HexColor("#16324F"), colors.HexColor("#1E40AF"), colors.HexColor("#EFF6FF"), colors.HexColor("#1E293B")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=navy, alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=10.5, leading=15, textColor=colors.HexColor("#475569"), alignment=TA_CENTER, spaceAfter=20))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=navy, spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=blue, spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.4, leading=14, textColor=ink, spaceAfter=8))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.2, leading=11, textColor=colors.HexColor("#475569"), spaceAfter=5))

def p(text, style="Bodyx"): return Paragraph(text, styles[style])
def table(rows, widths=None):
    t = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), navy), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8.2),
        ("LEADING", (0,0), (-1,-1), 10), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0,1), (-1,-1), colors.white), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, pale]),
        ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    return t

def footer(canvas, doc):
    canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#CBD5E1")); canvas.line(50, 35, A4[0]-50, 35)
    canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#64748B")); canvas.drawString(50, 22, "GigBid R&D report | AI-4016 | Attributed corpus + synthetic pilot")
    canvas.drawRightString(A4[0]-50, 22, f"Page {doc.page}"); canvas.restoreState()

story = []
story += [Spacer(1, 1.0*inch), p("GigBid", "ReportTitle"), p("R&D report for a human-approved freelancer copilot", "Sub"),
          p("AI-4016 | Individual assignment | Student submission draft", "Sub"), Spacer(1, .25*inch)]
story += [p("Executive summary", "H1x"), p("GigBid is a local-first web application that turns a freelance job post into a reviewable recommendation. It analyses fit, flags scam and prompt-injection patterns, retrieves portfolio evidence, proposes a price, drafts a proposal, checks claims, and pauses for human approval before a marketplace write. The system was built to make the important decision artefacts visible rather than to hide them behind a chat transcript."),
          p("The submitted implementation includes a redacted, attributed 250-record technical-job research sample derived from the Kaggle Upwork Job Postings Dataset 2024 (ODC-By), plus a separate synthetic three-job workflow/evaluation corpus. The pilot establishes functional behaviour only. It is not evidence of real Upwork performance, response rate, hire rate, model quality, or a completed hidden-set evaluation."),
          p("Research questions", "H1x"),
          p("A. Does tool design make the system safer and more inspectable? B. Does evidence-first retrieval improve grounding compared with a naive baseline? C. Is an explicit workflow better suited to this safety-critical task than unconstrained tool use?"),
          p("System design", "H1x"), p("The browser client is React and TypeScript; the service boundary is FastAPI. The application uses typed Pydantic handoffs for JobSpec, RiskReport, FitReport, PriceQuote, Decision, ProposalDraft, and ClaimCheck. A MarketplacePort hides whether the system is using the synthetic demo adapter or a future OAuth-protected official MCP adapter."),
          table([["Role", "Responsibility", "Output"], ["Scout", "Loads saved-search jobs", "Job candidate"], ["Analyst", "Extracts requirements and budget", "JobSpec"], ["Risk", "Detects scam, off-platform, injection cues", "RiskReport"], ["Fit", "Maps requirements to evidence", "FitReport"], ["Pricing", "Produces conservative quote", "PriceQuote"], ["Writer / verifier", "Drafts then labels claims", "ProposalDraft / ClaimCheck"], ["Compliance", "Blocks prohibited language", "Approval-ready draft"]], [1.05*inch, 3.15*inch, 2.2*inch])]
story += [p("Safety and approval boundary", "H1x"), p("A job post is data, not an instruction. The risk stage checks planted phrases such as requests for off-platform contact, free sample work, or instructions to ignore platform rules. A proposal can only become an approval-ready draft after evidence retrieval and claim verification. The approval endpoint requires an idempotency key and returns a dry-run preview; the demo never transmits a proposal."),
          p("MCP tool layer", "H1x"), p("Three owned MCP servers are included. The read-only Portfolio server offers search_evidence, get_case_study, list_skills, a portfolio resource, and a prompt template. The Marketplace server exposes read tools plus a draft preview with idempotency. The Workspace server is a deliberately local mock for calendar slots and email drafts. Agents would receive only the named tools required by their role.")]
story += [p("RAG approach", "H1x"), p("The repository includes configurable entry points for V0 naive retrieval, V1 requirement decomposition, V2 hybrid retrieval, V3 reranking, V4 outcome-aware ranking, and V8 corrective retrieval. The current deterministic demo scorer is intentionally transparent: it ranks lexical overlap and adds a small bonus for previously won portfolio artefacts in outcome-aware modes. It is an implementation scaffold, not a trained cross-encoder experiment."),
          table([["Variant", "Purpose", "Status in this submission"], ["V0", "Naive fixed retrieval baseline", "Implemented interface"], ["V1", "Requirement decomposition", "Implemented interface"], ["V2", "Hybrid evidence retrieval", "Selected demo default"], ["V3", "Cross-encoder reranking", "Interface only; needs open reranker"], ["V4", "Outcome-aware ranking", "Deterministic outcome bonus"], ["V8", "Corrective / self-RAG", "Interface only; needs graph loop"]], [0.6*inch, 2.5*inch, 3.3*inch]),
          p("Claim verification", "H2x"), p("Proposal sentences are split into claims. Claims that contain unsupported superlatives or guarantees are marked unsupported; claims that share a cited project skill are marked supported; remaining sentences are marked partly supported. This conservative rule is easier to audit than an uncalibrated judge, but it cannot understand paraphrase or subtle factual contradictions. The next experiment should compare a local NLI verifier with manually labelled claim evidence."),
          p("Data and evaluation method", "H1x"), p("The attributed research sample is imported by scripts/import_upwork_2024.py with per-record provenance, obvious contact-detail redaction, and no invented client histories or outcomes. The pilot uses three separate synthetic jobs: two suitable jobs and one deliberately unsafe prompt-injection/scam example. The evaluation runner exercises the complete deterministic workflow and writes a versioned JSON result. Expected decisions were authored with the synthetic data, so the accuracy figure is a smoke-test assertion rather than a generalisable estimate."),
          table([["Metric", "Pilot result", "Interpretation"], ["Jobs", "3 synthetic", "Too small for inference"], ["Decision accuracy", "1.00", "All three expected decisions matched"], ["Evidence Recall@5", "1.00", "Constructed corpus check, not a benchmark"], ["nDCG@10", "0.93", "Synthetic ranking proxy"], ["Unsupported claims", "0.00", "Per proposal; rule-based verifier on two drafts"], ["p95 latency", "0.18 s", "Local deterministic path"], ["Cost / proposal", "$0.00", "No hosted model used"]], [1.45*inch, 1.35*inch, 3.55*inch]),
          p("These values come from evals/results/demo_eval.json and can be regenerated with python evals/runners/run_demo_eval.py.", "Small")]
story += [p("Results and interpretation", "H1x"), p("The pilot confirms the system's intended control flow: benign jobs reach a visible approval gate, while the unsafe job is skipped before drafting. It also confirms that the UI can surface risk, evidence, claim status, pricing rationale, and a dry-run cost. It does not establish that hybrid retrieval beats V0, that a multi-agent system beats a single agent, or that the proposal will receive replies. Those are course-scale experiments requiring the supplied GigSim development set and held-out test infrastructure."),
          p("Threats to validity", "H2x"), p("The real job sample is historical, limited to technical postings, and lacks reliable outcomes; the portfolio and decision labels used in the executable pilot are synthetic and extremely small. Retrieval metrics are not derived from a blinded evidence annotation. The proposal judge is not calibrated. Latency excludes real model calls, network traffic, MCP transport, persistence, and queueing. For these reasons, the report deliberately avoids claims about business value or marketplace success."),
          p("Production plan", "H1x"), p("The next step is to replace the JSON adapter with the course GigSim adapter while preserving MarketplacePort. I would add PostgreSQL checkpointing, Redis-backed worker scheduling, encrypted OAuth token storage, per-user tenant filters, OpenTelemetry tracing, and tests that kill and resume a waiting run. For measured RAG, I would ingest only consented portfolio assets, label a development set, compare V0/V1/V2/V3/V4/V8 per persona, and select the deployed configuration by evidence recall, unsupported claims, latency, and cost. Live mode would remain draft-only and require the official Upwork MCP server, not browser automation."),
          p("Conclusion", "H1x"), p("GigBid's contribution is not autonomous bidding. It is a reviewable decision pipeline that makes evidence, risk, price, and approval explicit. The synthetic pilot is a reliable local demonstration of those controls. Replacing the toy corpus with GigSim and completing the outlined experiments is necessary before treating the result as an evaluated marketplace system.")]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=50, leftMargin=50, topMargin=48, bottomMargin=48, title="GigBid R&D report")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
