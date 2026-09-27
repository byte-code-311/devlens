from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BugReport(Base):
    __tablename__ = "bug_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expected_behavior: Mapped[str] = mapped_column(Text, nullable=False)
    actual_behavior: Mapped[str] = mapped_column(Text, nullable=False)
    reproduction_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    triage_runs: Mapped[list["TriageRun"]] = relationship(back_populates="report")


class EvidenceChunk(Base):
    __tablename__ = "evidence_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(300), nullable=False)
    location: Mapped[str] = mapped_column(String(120), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class TriageRun(Base):
    __tablename__ = "triage_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("bug_reports.id"), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    hypotheses_json: Mapped[str] = mapped_column(Text, nullable=False)
    test_suggestions_json: Mapped[str] = mapped_column(Text, nullable=False)
    limitations_json: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_ids_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    report: Mapped[BugReport] = relationship(back_populates="triage_runs")
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="triage_run")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    triage_id: Mapped[int] = mapped_column(ForeignKey("triage_runs.id"), nullable=False)
    helpful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    triage_run: Mapped[TriageRun] = relationship(back_populates="feedback")
