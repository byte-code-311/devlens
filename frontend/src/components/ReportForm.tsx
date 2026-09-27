import { useState, type FormEvent } from "react";
import { createReport } from "../api/client";
import { ApiError, type BugReport, type BugReportCreate } from "../types";

type Props = { onCreated: (report: BugReport) => void };
const blank: BugReportCreate = { title: "", description: "", expected_behavior: "", actual_behavior: "", reproduction_steps: "" };

export default function ReportForm({ onCreated }: Props) {
  const [form, setForm] = useState(blank);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (field: keyof BugReportCreate, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
    setFieldErrors((current) => ({ ...current, [field]: "" }));
  };

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setFieldErrors({});
    try {
      const saved = await createReport({ ...form, reproduction_steps: form.reproduction_steps?.trim() || null });
      setForm(blank);
      onCreated(saved);
    } catch (reason) {
      if (reason instanceof ApiError) setFieldErrors(reason.fieldErrors);
      setError(reason instanceof Error ? reason.message : "The report could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="panel report-form" onSubmit={handleSubmit}>
      <div className="panel-heading"><div><span className="section-kicker">NEW REPORT</span><h2>Describe the bug</h2></div><span className="required-note">* Required</span></div>
      <label>Title<input value={form.title} onChange={(e) => set("title", e.target.value)} maxLength={160} placeholder="A short, clear summary" aria-invalid={Boolean(fieldErrors.title)} /></label>
      {fieldErrors.title && <small className="field-error">{fieldErrors.title}</small>}
      <label>Description<textarea value={form.description} onChange={(e) => set("description", e.target.value)} rows={3} maxLength={5000} placeholder="What happened?" aria-invalid={Boolean(fieldErrors.description)} /></label>
      {fieldErrors.description && <small className="field-error">{fieldErrors.description}</small>}
      <label>Expected behavior<textarea value={form.expected_behavior} onChange={(e) => set("expected_behavior", e.target.value)} rows={2} maxLength={5000} placeholder="What should happen?" aria-invalid={Boolean(fieldErrors.expected_behavior)} /></label>
      {fieldErrors.expected_behavior && <small className="field-error">{fieldErrors.expected_behavior}</small>}
      <label>Actual behavior<textarea value={form.actual_behavior} onChange={(e) => set("actual_behavior", e.target.value)} rows={2} maxLength={5000} placeholder="What happens instead?" aria-invalid={Boolean(fieldErrors.actual_behavior)} /></label>
      {fieldErrors.actual_behavior && <small className="field-error">{fieldErrors.actual_behavior}</small>}
      <label>Reproduction steps (optional)<textarea value={form.reproduction_steps ?? ""} onChange={(e) => set("reproduction_steps", e.target.value)} rows={2} maxLength={5000} placeholder="1. Open the page…" /></label>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="primary-button full-width" type="submit" disabled={busy}>{busy ? "Saving…" : "Create report"}</button>
    </form>
  );
}
