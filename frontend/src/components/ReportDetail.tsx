import type { BugReport, TriageRun } from "../types";
import TriagePanel from "./TriagePanel";

type Props = { report: BugReport | null; triage: TriageRun | null; busy: boolean; error: string; onRun: () => void };

export default function ReportDetail({ report, triage, busy, error, onRun }: Props) {
  if (!report) return <section className="panel detail-empty"><div className="empty-icon">⌕</div><h2>Select a report to begin</h2><p>Create a bug report or choose one from your recent reports to inspect evidence-backed triage.</p></section>;
  return <div className="detail-column">
    <section className="panel report-detail">
      <div className="detail-title-row"><div><span className="section-kicker">BUG REPORT #{report.id}</span><h2>{report.title}</h2></div><span className="open-pill"><span className="status-dot" /> Open</span></div>
      <p className="report-description">{report.description}</p>
      <div className="behavior-grid"><div><span className="mini-label">EXPECTED</span><p>{report.expected_behavior}</p></div><div><span className="mini-label">ACTUAL</span><p>{report.actual_behavior}</p></div></div>
      {report.reproduction_steps && <div className="reproduction"><span className="mini-label">REPRODUCTION</span><p>{report.reproduction_steps}</p></div>}
    </section>
    <TriagePanel triage={triage} busy={busy} error={error} onRun={onRun} />
  </div>;
}
