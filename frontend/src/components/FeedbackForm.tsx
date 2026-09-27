import { useState } from "react";
import { submitFeedback } from "../api/client";

type Props = { triageId: number };

export default function FeedbackForm({ triageId }: Props) {
  const [helpful, setHelpful] = useState<boolean | null>(null);
  const [comment, setComment] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function send() {
    if (helpful === null) return;
    setBusy(true);
    setError("");
    try {
      await submitFeedback(triageId, { helpful, comment: comment.trim() || null });
      setSent(true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Feedback could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  if (sent) return <p className="feedback-success" role="status">Thanks — your feedback was saved.</p>;
  return <div className="feedback-box">
    <div className="feedback-question">Was this triage useful?</div>
    <div className="feedback-actions">
      <button className={`choice-button ${helpful === true ? "chosen" : ""}`} onClick={() => setHelpful(true)}>Helpful</button>
      <button className={`choice-button ${helpful === false ? "chosen" : ""}`} onClick={() => setHelpful(false)}>Not helpful</button>
      <button className="send-feedback" onClick={send} disabled={helpful === null || busy}>{busy ? "Sending…" : "Send feedback"}</button>
    </div>
    <label className="feedback-comment">Comment (optional)<textarea value={comment} onChange={(event) => setComment(event.target.value)} maxLength={2000} rows={2} placeholder="What worked or what was missing?" /></label>
    {error && <p role="alert" className="form-error">{error}</p>}
  </div>;
}
