from typing import Protocol

from ...schemas import BugReportRead, EvidenceChunkRead, TriageOutput


class ProviderError(RuntimeError):
    """A configured triage provider could not return a valid response."""


class TriageProvider(Protocol):
    mode: str

    def generate(
        self, report: BugReportRead, evidence: list[EvidenceChunkRead]
    ) -> TriageOutput: ...
