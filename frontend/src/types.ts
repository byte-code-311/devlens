export type BugReport = {
  id: number;
  title: string;
  description: string;
  expected_behavior: string;
  actual_behavior: string;
  reproduction_steps: string | null;
  created_at: string;
};

export type BugReportCreate = Omit<BugReport, "id" | "created_at">;

export type EvidenceChunk = {
  id: number;
  source: string;
  location: string;
  text: string;
  score: number;
};

export type TriageSuggestion = { text: string; evidence_ids: number[] };

export type TriageRun = {
  id: number;
  report_id: number;
  mode: "baseline" | "ai";
  created_at: string;
  summary: string;
  hypotheses: TriageSuggestion[];
  test_suggestions: TriageSuggestion[];
  limitations: string[];
  evidence: EvidenceChunk[];
};

export type FeedbackCreate = { helpful: boolean; comment: string | null };
export type Feedback = FeedbackCreate & { id: number; triage_id: number; created_at: string };

export class ApiError extends Error {
  constructor(
    message: string,
    readonly fieldErrors: Record<string, string> = {},
  ) {
    super(message);
    this.name = "ApiError";
  }
}
