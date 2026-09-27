from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BugReportCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=10, max_length=5000)
    expected_behavior: str = Field(min_length=10, max_length=5000)
    actual_behavior: str = Field(min_length=10, max_length=5000)
    reproduction_steps: str | None = Field(default=None, max_length=5000)

    @field_validator(
        "title",
        "description",
        "expected_behavior",
        "actual_behavior",
        "reproduction_steps",
        mode="before",
    )
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        return value.strip() if isinstance(value, str) else value


class BugReportRead(BugReportCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EvidenceChunkRead(BaseModel):
    id: int
    source: str
    location: str
    text: str
    score: float


class Hypothesis(BaseModel):
    text: str
    evidence_ids: list[int]


class TestSuggestion(BaseModel):
    text: str
    evidence_ids: list[int]


class TriageOutput(BaseModel):
    summary: str
    hypotheses: list[Hypothesis]
    test_suggestions: list[TestSuggestion]
    limitations: list[str]


class TriageRunRead(TriageOutput):
    id: int
    report_id: int
    mode: str
    created_at: datetime
    evidence: list[EvidenceChunkRead]


class FeedbackCreate(BaseModel):
    helpful: bool
    comment: str | None = Field(default=None, max_length=2000)


class FeedbackRead(FeedbackCreate):
    id: int
    triage_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
