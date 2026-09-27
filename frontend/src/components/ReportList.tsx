import type { BugReport } from "../types";

type Props = { reports: BugReport[]; selectedId: number | null; onSelect: (id: number) => void };

export default function ReportList({ reports, selectedId, onSelect }: Props) {
  return (
    <section className="panel report-list">
      <div className="panel-heading"><div><span className="section-kicker">INBOX</span><h2>Recent reports</h2></div><span className="list-count">{reports.length}</span></div>
      {reports.length === 0 ? <p className="muted small-copy">Your reports will appear here.</p> : (
        <ul>{reports.map((report) => <li key={report.id}>
          <button className={`report-row ${report.id === selectedId ? "selected" : ""}`} onClick={() => onSelect(report.id)} aria-label={`Open report ${report.title}`}>
            <span className="report-row-icon">!</span><span className="report-row-copy"><strong>{report.title}</strong><small>{new Date(report.created_at).toLocaleDateString()}</small></span><span className="row-chevron">›</span>
          </button>
        </li>)}</ul>
      )}
    </section>
  );
}
