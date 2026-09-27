import { ApiError, type BugReport, type BugReportCreate, type Feedback, type FeedbackCreate, type TriageRun } from "../types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new Error("Could not reach the DevLens API. Start the backend and try again.");
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const fieldErrors: Record<string, string> = {};
    if (Array.isArray(data.detail)) {
      for (const issue of data.detail) {
        const field = issue.loc?.at(-1);
        if (typeof field === "string") fieldErrors[field] = issue.msg;
      }
    }
    const message = fieldErrors && Object.keys(fieldErrors).length
      ? "Please correct the highlighted fields."
      : typeof data.detail === "string" ? data.detail : "The request could not be completed.";
    throw new ApiError(message, fieldErrors);
  }
  return data as T;
}

export const listReports = () => request<BugReport[]>("/reports");
export const createReport = (payload: BugReportCreate) => request<BugReport>("/reports", { method: "POST", body: JSON.stringify(payload) });
export const getTriageHistory = (reportId: number) => request<TriageRun[]>(`/reports/${reportId}/triage`);
export const requestTriage = (reportId: number) => request<TriageRun>(`/reports/${reportId}/triage`, { method: "POST" });
export const submitFeedback = (triageId: number, payload: FeedbackCreate) => request<Feedback>(`/triage/${triageId}/feedback`, { method: "POST", body: JSON.stringify(payload) });
