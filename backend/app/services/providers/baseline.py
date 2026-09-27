from ...schemas import (
    BugReportRead,
    EvidenceChunkRead,
    Hypothesis,
    TestSuggestion,
    TriageOutput,
)


class BaselineProvider:
    mode = "baseline"

    def generate(
        self, report: BugReportRead, evidence: list[EvidenceChunkRead]
    ) -> TriageOutput:
        if not evidence:
            return TriageOutput(
                summary=f"Start by reproducing: {report.title}",
                hypotheses=[],
                test_suggestions=[
                    TestSuggestion(
                        text="Add a regression test that reproduces the actual behavior and asserts the expected behavior.",
                        evidence_ids=[],
                    )
                ],
                limitations=[
                    "No relevant code or issue evidence was found, so cause hypotheses are withheld."
                ],
            )

        top_evidence = evidence[:3]
        return TriageOutput(
            summary=f"Review the retrieved material around: {report.title}",
            hypotheses=[
                Hypothesis(
                    text="This code path or related report may be a useful starting point for investigating the reported behavior.",
                    evidence_ids=[chunk.id],
                )
                for chunk in top_evidence
            ],
            test_suggestions=[
                TestSuggestion(
                    text="Add a regression test for the reported behavior around this source location.",
                    evidence_ids=[chunk.id],
                )
                for chunk in top_evidence[:1]
            ],
            limitations=[
                "Baseline mode uses keyword matches and does not infer a confirmed root cause."
            ],
        )
