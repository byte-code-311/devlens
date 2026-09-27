import type { TriageRun } from "../types";
import FeedbackForm from "./FeedbackForm";

type Props = { triage: TriageRun | null; busy: boolean; error: string; onRun: () => void };

export default function TriagePanel({ triage, busy, error, onRun }: Props) {
  return (
    <section className="panel triage-panel">
      <div className="panel-heading"><div><span className="section-kicker">ANALYSIS</span><h2>Evidence-backed triage</h2></div>{triage && <span className={`mode-pill ${triage.mode}`}>{triage.mode === "ai" ? "AI-assisted" : "Baseline mode"}</span>}</div>
      {!triage ? <div className="triage-empty"><div className="spark-icon">✳</div><p>Run triage to search the sample code and related reports for clues.</p><button className="primary-button" onClick={onRun} disabled={busy}>{busy ? "Reviewing evidence…" : "Run triage"}</button>{error && <p className="form-error" role="alert">{error}</p>}</div> : <div className="triage-content">
        <div className="triage-summary"><span className="mini-label">SUMMARY</span><p>{triage.summary}</p></div>
        {triage.hypotheses.length > 0 && <div className="triage-section"><span className="mini-label">POSSIBLE LEADS</span><ul className="suggestion-list">{triage.hypotheses.map((item, index) => <li key={`${item.text}-${index}`}>{item.text}<small>{item.evidence_ids.map((id) => `Evidence ${id}`).join(" · ")}</small></li>)}</ul></div>}
        <div className="triage-section"><span className="mini-label">TEST IDEAS</span>{triage.test_suggestions.length ? <ul className="suggestion-list">{triage.test_suggestions.map((item, index) => <li key={`${item.text}-${index}`}>{item.text}<small>{item.evidence_ids.length ? item.evidence_ids.map((id) => `Evidence ${id}`).join(" · ") : "General regression test"}</small></li>)}</ul> : <p className="muted small-copy">No test ideas were returned.</p>}</div>
        <div className="triage-section"><span className="mini-label">SUPPORTING EVIDENCE <span className="evidence-count">{triage.evidence.length}</span></span>
          {triage.evidence.length ? <div className="evidence-list">{triage.evidence.map((item) => <article className="evidence-card" key={item.id}><div className="evidence-source"><span className="file-mark">⌘</span><span><strong>{item.source}</strong><small>Lines {item.location}</small></span></div><pre>{item.text}</pre></article>)}</div> : <p className="low-evidence">No matching sources found. Cause hypotheses were withheld.</p>}
        </div>
        {triage.limitations.length > 0 && <div className="limitations"><span>ⓘ</span><div><strong>Keep in mind</strong>{triage.limitations.map((item) => <p key={item}>{item}</p>)}</div></div>}
        <FeedbackForm key={triage.id} triageId={triage.id} />
      </div>}
    </section>
  );
}
