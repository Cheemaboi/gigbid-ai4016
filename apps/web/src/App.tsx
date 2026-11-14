import { useEffect, useMemo, useState } from "react";

type Job = { id: string; title: string; description: string; skills: string[]; budget: number; connects_cost: number; client: string; fit_score: number; risk_score: number; recommendation: "bid" | "skip" | "watch"; recommended_bid: number };
type Evidence = { id: string; title: string; excerpt: string; skills: string[]; outcome: string };
type Analysis = { risk: { score: number; is_scam: boolean; flags: string[]; rationale: string }; fit: { score: number; evidence: Evidence[]; gaps: string[] }; price: { recommended_bid: number; rationale: string }; decision: { action: string; reason: string } };
type Draft = { id: string; body: string; price: number; status: string; claims: { claim: string; status: string; evidence_ids: string[] }[]; dry_run_preview?: { connects_cost: number } };
type Run = { analysis: Analysis; draft?: Draft; events: string[] };
const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function classForRisk(score: number) { return score >= 70 ? "danger" : score >= 35 ? "warning" : "safe"; }

export default function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedId, setSelectedId] = useState("job-1001");
  const [run, setRun] = useState<Run | null>(null);
  const [draftText, setDraftText] = useState("");
  const [state, setState] = useState<"loading" | "ready" | "running" | "error">("loading");
  const [notice, setNotice] = useState("Loading locally seeded jobs...");

  const selected = useMemo(() => jobs.find((job) => job.id === selectedId), [jobs, selectedId]);
  useEffect(() => { void loadJobs(); }, []);
  async function loadJobs() {
    setState("loading");
    try { const response = await fetch(`${API}/jobs`); if (!response.ok) throw new Error(); setJobs(await response.json()); setState("ready"); setNotice("Demo marketplace is available. Nothing is sent automatically."); }
    catch { setState("error"); setNotice("Marketplace unavailable. Check that the FastAPI server is running, then retry."); }
  }
  async function runAgents() {
    if (!selected) return;
    setState("running"); setNotice("Running Scout, Analyst, Risk and Fit checks...");
    try { const response = await fetch(`${API}/jobs/${selected.id}/run`, { method: "POST" }); if (!response.ok) throw new Error(); const result: Run = await response.json(); setRun(result); setDraftText(result.draft?.body ?? ""); setState("ready"); setNotice(result.draft ? "Draft paused for your approval." : "This job was safely skipped. Review the risk report."); }
    catch { setState("error"); setNotice("The agent run could not complete. Your work is not sent or lost."); }
  }
  async function approve() {
    if (!run?.draft) return;
    setState("running");
    const response = await fetch(`${API}/proposals/${run.draft.id}/approve`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ edited_body: draftText, idempotency_key: `ui-${run.draft.id}` }) });
    if (!response.ok) { setState("error"); setNotice("Approval could not be recorded. Please retry."); return; }
    const approved: Draft = await response.json(); setRun({ ...run, draft: approved }); setState("ready"); setNotice(`Approval saved. Preview only: ${approved.dry_run_preview?.connects_cost ?? 0} Connects would be used.`);
  }
  function reject() { if (!run?.draft) return; setRun({ ...run, draft: { ...run.draft, status: "rejected" } }); setNotice("Draft rejected locally. No action reached a client."); }

  return <div className="min-h-[100dvh] bg-[var(--surface)] text-[var(--ink)]">
    <a href="#main" className="skip-link">Skip to content</a>
    <header className="border-b border-[var(--border)] bg-white"><div className="mx-auto flex max-w-[1440px] items-center justify-between gap-6 px-4 py-4 lg:px-8"><div><p className="font-mono text-xs font-bold tracking-[0.16em] text-[var(--primary)]">GIGBID / REVIEW MODE</p><h1 className="text-xl font-semibold tracking-tight">Freelance decisions with receipts.</h1></div><nav aria-label="Primary navigation" className="hidden gap-5 text-sm font-medium text-slate-600 md:flex"><a href="#inbox">Job inbox</a><a href="#studio">Proposal studio</a><a href="#analytics">Analytics</a></nav><span className="rounded-full border border-[var(--border)] bg-blue-50 px-3 py-1 text-xs font-semibold text-[var(--primary)]">Local demo</span></div></header>
    <main id="main" className="mx-auto max-w-[1440px] px-4 py-6 lg:px-8">
      <section aria-live="polite" className={`mb-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border px-4 py-3 ${state === "error" ? "border-red-200 bg-red-50 text-red-800" : "border-blue-100 bg-white text-slate-700"}`}><p className="text-sm"><strong>{state === "error" ? "Attention: " : "Status: "}</strong>{notice}</p><button onClick={() => void loadJobs()} className="text-sm font-semibold text-[var(--primary)] underline underline-offset-4">Refresh jobs</button></section>
      <div className="grid gap-6 xl:grid-cols-[0.85fr_1.55fr_0.9fr]">
        <section id="inbox" aria-labelledby="inbox-heading" className="panel"><div className="panel-header"><div><p className="eyebrow">Inbox</p><h2 id="inbox-heading">Ranked work</h2></div><span className="metric">{jobs.length} jobs</span></div><div className="divide-y divide-[var(--border)]">{jobs.map((job) => <button key={job.id} onClick={() => { setSelectedId(job.id); setRun(null); }} className={`job-row ${selectedId === job.id ? "selected" : ""}`}><span className="flex items-start justify-between gap-3"><strong>{job.title}</strong><span className={`status ${classForRisk(job.risk_score)}`}>{job.recommendation}</span></span><span className="mt-2 flex justify-between text-xs text-slate-500"><span>{job.client}</span><span>Fit {job.fit_score}</span></span></button>)}</div></section>
        <section className="space-y-6"><section className="panel" aria-labelledby="job-heading"><div className="panel-header"><div><p className="eyebrow">Job detail</p><h2 id="job-heading">{selected?.title ?? "Choose a job"}</h2></div>{selected && <span className={`status ${classForRisk(selected.risk_score)}`}>Risk {selected.risk_score}</span>}</div>{selected && <><p className="max-w-[72ch] text-sm leading-6 text-slate-700">{selected.description}</p><div className="mt-5 flex flex-wrap gap-2">{selected.skills.map((skill) => <span key={skill} className="tag">{skill}</span>)}</div><dl className="mt-6 grid grid-cols-3 gap-3"><div><dt>Budget</dt><dd>${selected.budget}</dd></div><div><dt>Suggested bid</dt><dd>${selected.recommended_bid}</dd></div><div><dt>Connects</dt><dd>{selected.connects_cost}</dd></div></dl><button disabled={state === "running"} onClick={() => void runAgents()} className="primary-button mt-6">{state === "running" ? "Running checks..." : "Run safe analysis"}</button></>}</section>
          {run && <section className="panel" aria-labelledby="analysis-heading"><div className="panel-header"><div><p className="eyebrow">Agent run</p><h2 id="analysis-heading">Decision trail</h2></div><span className={`status ${run.analysis.decision.action === "bid" ? "safe" : "danger"}`}>{run.analysis.decision.action}</span></div><ol className="timeline">{run.events.map((event, index) => <li key={event}><span>{index + 1}</span>{event}</li>)}</ol><div className="analysis-grid"><article><h3>Risk assessment</h3><p>{run.analysis.risk.rationale}</p>{run.analysis.risk.flags.map((flag) => <span className="tag danger" key={flag}>{flag}</span>)}</article><article><h3>Price rationale</h3><p>{run.analysis.price.rationale}</p></article></div></section>}</section>
        <aside className="space-y-6"><section className="panel" aria-labelledby="evidence-heading"><div className="panel-header"><div><p className="eyebrow">Grounding</p><h2 id="evidence-heading">Evidence matrix</h2></div></div>{run ? <div className="space-y-3">{run.analysis.fit.evidence.map((item) => <article key={item.id} className="evidence"><p className="font-semibold text-slate-900">{item.title}</p><p>{item.excerpt}</p><span>{item.outcome.replace("_", " ")}</span></article>)}</div> : <p className="text-sm text-slate-600">Run an analysis to match job requirements against the synthetic portfolio.</p>}</section><section id="analytics" className="panel"><p className="eyebrow">Budget guardrail</p><h2>Weekly Connects</h2><div className="mt-4 flex items-baseline justify-between"><strong className="text-3xl">40</strong><span className="text-sm text-slate-500">of 40 remaining</span></div><div className="meter"><span /></div><p className="mt-3 text-xs leading-5 text-slate-600">No Connects are spent by this demo. Approval produces a transparent dry-run preview.</p></section></aside>
      </div>
      {run?.draft && <section id="studio" className="mt-6 panel" aria-labelledby="studio-heading"><div className="panel-header"><div><p className="eyebrow">Human approval gate</p><h2 id="studio-heading">Proposal studio</h2></div><span className={`status ${run.draft.status === "approved" ? "safe" : run.draft.status === "rejected" ? "danger" : "warning"}`}>{run.draft.status.replace("_", " ")}</span></div><div className="grid gap-6 lg:grid-cols-[1.45fr_0.85fr]"><div><label htmlFor="draft" className="label">Proposal draft</label><textarea id="draft" value={draftText} onChange={(event) => setDraftText(event.target.value)} disabled={run.draft.status !== "awaiting_approval"} className="draft-editor" /><div className="mt-4 flex flex-wrap gap-3"><button disabled={run.draft.status !== "awaiting_approval" || state === "running"} onClick={() => void approve()} className="primary-button">Approve dry-run draft</button><button disabled={run.draft.status !== "awaiting_approval"} onClick={reject} className="secondary-button">Reject with reason</button></div></div><div><h3 className="text-sm font-semibold">Claim checks</h3><ul className="mt-3 space-y-3">{run.draft.claims.map((claim, index) => <li key={index} className="claim"><span className={`status ${claim.status === "supported" ? "safe" : "warning"}`}>{claim.status}</span><p>{claim.claim}</p>{claim.evidence_ids.length > 0 && <small>Evidence: {claim.evidence_ids.join(", ")}</small>}</li>)}</ul></div></div></section>}
    </main>
  </div>;
}

