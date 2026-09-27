import { beforeEach, describe, expect, it, vi } from "vitest";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "../App";
import * as api from "../api/client";
import { ApiError, type BugReport, type TriageRun } from "../types";

vi.mock("../api/client", () => ({
  listReports: vi.fn(),
  createReport: vi.fn(),
  getTriageHistory: vi.fn(),
  requestTriage: vi.fn(),
  submitFeedback: vi.fn(),
}));

const report: BugReport = {
  id: 7,
  title: "Search filter clears the list",
  description: "The list becomes empty after choosing a search filter.",
  expected_behavior: "Matching items should remain in the list.",
  actual_behavior: "The list becomes empty after filtering.",
  reproduction_steps: "Open search and choose a filter.",
  created_at: "2026-09-27T10:00:00Z",
};

const otherReport: BugReport = {
  ...report,
  id: 8,
  title: "Export button does nothing",
  created_at: "2026-09-27T10:01:00Z",
};

const triage: TriageRun = {
  id: 4,
  report_id: 7,
  mode: "baseline",
  created_at: "2026-09-27T10:05:00Z",
  summary: "Review the search filter path.",
  hypotheses: [{ text: "The filter state may be relevant.", evidence_ids: [2] }],
  test_suggestions: [{ text: "Add a filter regression test.", evidence_ids: [2] }],
  limitations: ["Keyword matches do not confirm a root cause."],
  evidence: [{ id: 2, source: "sample-app/src/search/view.py", location: "41-53", text: "state.results = []", score: 2 }],
};

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.listReports).mockResolvedValue([]);
  vi.mocked(api.getTriageHistory).mockResolvedValue([]);
});

describe("DevLens report flow", () => {
  it("submits a report and displays it in the workspace", async () => {
    vi.mocked(api.createReport).mockResolvedValue(report);
    render(<App />);
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: report.title } });
    fireEvent.change(screen.getByLabelText("Description"), { target: { value: report.description } });
    fireEvent.change(screen.getByLabelText("Expected behavior"), { target: { value: report.expected_behavior } });
    fireEvent.change(screen.getByLabelText("Actual behavior"), { target: { value: report.actual_behavior } });
    fireEvent.change(screen.getByLabelText("Reproduction steps (optional)"), { target: { value: report.reproduction_steps } });
    fireEvent.click(screen.getByRole("button", { name: "Create report" }));

    expect(await screen.findAllByText(report.title)).not.toHaveLength(0);
    expect(api.createReport).toHaveBeenCalledWith(expect.objectContaining({ title: report.title }));
  });

  it("shows field validation errors and keeps the form editable", async () => {
    vi.mocked(api.createReport).mockRejectedValue(new ApiError("Please correct the highlighted fields.", { title: "Use at least 3 characters." }));
    render(<App />);
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "x" } });
    fireEvent.click(screen.getByRole("button", { name: "Create report" }));

    expect(await screen.findByText("Use at least 3 characters.")).toBeInTheDocument();
    expect(screen.getByLabelText("Title")).toBeEnabled();
  });

  it("renders triage mode, evidence source, and cited snippet", async () => {
    vi.mocked(api.listReports).mockResolvedValue([report]);
    vi.mocked(api.requestTriage).mockResolvedValue(triage);
    let resolveHistory!: (items: TriageRun[]) => void;
    vi.mocked(api.getTriageHistory).mockImplementation(() => new Promise((resolve) => { resolveHistory = resolve; }));
    render(<App />);
    await waitFor(() => expect(api.getTriageHistory).toHaveBeenCalledWith(report.id));
    fireEvent.click(await screen.findByRole("button", { name: /run triage/i }));

    expect(await screen.findByText("Review the search filter path.")).toBeInTheDocument();
    await act(async () => { resolveHistory([]); await Promise.resolve(); });
    expect(screen.getByText("Review the search filter path.")).toBeInTheDocument();
    expect(screen.getByText("Baseline mode")).toBeInTheDocument();
    expect(screen.getByText("sample-app/src/search/view.py")).toBeInTheDocument();
    expect(screen.getByText("state.results = []")).toBeInTheDocument();
  });

  it("does not show one report's triage while another report's history is loading", async () => {
    vi.mocked(api.listReports).mockResolvedValue([report, otherReport]);
    vi.mocked(api.getTriageHistory).mockImplementation((reportId) =>
      reportId === report.id ? Promise.resolve([triage]) : new Promise(() => {}),
    );
    render(<App />);

    expect(await screen.findByText("Review the search filter path.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: `Open report ${otherReport.title}` }));

    await waitFor(() => expect(api.getTriageHistory).toHaveBeenCalledWith(otherReport.id));
    expect(screen.queryByText("Review the search filter path.")).not.toBeInTheDocument();
    expect(screen.queryByText("sample-app/src/search/view.py")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Helpful" })).not.toBeInTheDocument();
  });

  it("submits helpful feedback for a triage run", async () => {
    vi.mocked(api.listReports).mockResolvedValue([report]);
    vi.mocked(api.getTriageHistory).mockResolvedValue([triage]);
    vi.mocked(api.submitFeedback).mockResolvedValue({ id: 5, triage_id: 4, helpful: true, comment: null, created_at: "2026-09-27T10:10:00Z" });
    render(<App />);
    fireEvent.click(await screen.findByRole("button", { name: "Helpful" }));
    fireEvent.click(screen.getByRole("button", { name: "Send feedback" }));

    await waitFor(() => expect(api.submitFeedback).toHaveBeenCalledWith(4, expect.objectContaining({ helpful: true })));
  });

  it("keeps the form usable and shows a clear message on network failure", async () => {
    vi.mocked(api.createReport).mockRejectedValue(new Error("Could not reach the DevLens API. Start the backend and try again."));
    render(<App />);
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: report.title } });
    fireEvent.click(screen.getByRole("button", { name: "Create report" }));

    expect(await screen.findByText(/could not reach the DevLens API/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Title")).toHaveValue(report.title);
    expect(screen.getByLabelText("Title")).toBeEnabled();
  });
});
