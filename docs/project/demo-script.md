# DevLens Demo and Viva Guide

## Five-minute demonstration

1. Start the backend and frontend using the README instructions. Show the seeded report list.
2. Open **Search results disappear after filtering** and review the expected and actual behavior.
3. Run triage in baseline mode. Point out the mode label, possible lead, test idea, and cited source path and lines.
4. Open the evidence snippet and explain that the citation is a stable corpus record returned by search.
5. Mark the triage helpful and submit feedback.
6. Create a new report with a topic that has no corpus match. Run triage and show the low-evidence limitation and the absence of a root-cause hypothesis.
7. Explain that an AI API key is optional; configured AI output is structured and its evidence IDs are validated server-side.

## Suggested viva questions

**What is the main contribution?** The system connects bug reports to inspectable code and issue evidence, and validates model references before showing them.

**Why include a baseline provider?** It makes the demo reproducible without API credentials and gives a stable comparison point for the optional AI mode.

**How do you prevent invented citations?** The provider receives a limited evidence set; the backend checks every returned evidence ID against that set before persisting the run.

**What are the limitations?** The corpus is small and retrieval is lexical, so relevant material may be missed. Suggestions are investigation aids, not verified diagnoses.

**How would you evaluate it?** Build a labeled set of reports with relevant source chunks, measure retrieval precision/recall, check citation validity, and collect reviewer ratings for usefulness and unsupported claims.
