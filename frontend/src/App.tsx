import { useEffect, useMemo, useRef, useState } from "react";
import { getTriageHistory, listReports, requestTriage } from "./api/client";
import ReportDetail from "./components/ReportDetail";
import ReportForm from "./components/ReportForm";
import ReportList from "./components/ReportList";
import { type BugReport, type TriageRun } from "./types";

function App() {
  const [reports, setReports] = useState<BugReport[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [triages, setTriages] = useState<TriageRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const selected = useMemo(() => reports.find((report) => report.id === selectedId) ?? null, [reports, selectedId]);
  const selectedIdRef = useRef(selectedId);

  useEffect(() => { selectedIdRef.current = selectedId; }, [selectedId]);

  useEffect(() => {
    let active = true;
    listReports().then((items) => {
      if (!active) return;
      setReports(items);
      setSelectedId((current) => current ?? items[0]?.id ?? null);
    }).catch((reason: unknown) => {
      if (active) setError(reason instanceof Error ? reason.message : "Reports could not be loaded.");
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (selectedId === null) { setTriages([]); return; }
    let active = true;
    getTriageHistory(selectedId).then((items) => {
      if (!active) return;
      setTriages((current) => {
        const merged = new Map(items.map((item) => [item.id, item]));
        current.filter((item) => item.report_id === selectedId).forEach((item) => merged.set(item.id, item));
        return [...merged.values()].sort((left, right) => Date.parse(right.created_at) - Date.parse(left.created_at));
      });
    })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : "Triage history could not be loaded."); });
    return () => { active = false; };
  }, [selectedId]);

  function handleCreated(saved: BugReport) {
    setReports((items) => [saved, ...items]);
    setSelectedId(saved.id);
  }

  async function handleRunTriage() {
    if (!selected) return;
    const reportId = selected.id;
    setBusy(true);
    setError("");
    try {
      const result = await requestTriage(reportId);
      if (selectedIdRef.current === reportId) setTriages((items) => [result, ...items]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Triage could not be completed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">D</span> DevLens</div>
        <div className="workspace-label">WORKSPACE</div>
        <div className="nav-item active"><span>▤</span> Bug reports <span className="count">{reports.length}</span></div>
        <div className="sidebar-bottom"><span className="status-dot" /> Local demo mode</div>
      </aside>
      <section className="main-area">
        <header className="topbar"><span>Workspace <span className="crumb">/</span> Bug reports</span><span className="avatar">D</span></header>
        <div className="content">
          <div className="eyebrow">TRIAGE WORKSPACE</div>
          <div className="hero-row"><div><h1>Bug reports</h1><p className="subtitle">Turn unclear reports into evidence-backed next steps.</p></div><a className="status-label" href="#new-report">＋ New report</a></div>
          {error && <div className="notice-error" role="alert">{error}</div>}
          <div className="workspace-grid">
            <div className="left-column">
              <div id="new-report"><ReportForm onCreated={handleCreated} /></div>
              <ReportList reports={reports} selectedId={selectedId} onSelect={(id) => { setError(""); setSelectedId(id); }} />
              {loading && <p className="muted small-copy loading-note">Loading reports…</p>}
            </div>
            <ReportDetail report={selected} triage={triages.find((run) => run.report_id === selectedId) ?? null} busy={busy} error={error} onRun={handleRunTriage} />
          </div>
          <footer className="app-footer"><span><span className="status-dot" /> Local demo mode</span><span>Suggestions cite sample code and issue evidence.</span></footer>
        </div>
      </section>
    </main>
  );
}

export default App;
