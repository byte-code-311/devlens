import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import BugReport, EvidenceChunk, Feedback, TriageRun
from ..schemas import (
    EvidenceChunkRead,
    FeedbackCreate,
    FeedbackRead,
    TriageOutput,
    TriageRunRead,
)
from .providers import get_provider
from .providers.base import ProviderError, TriageProvider
from .search import search_evidence


class ReportNotFoundError(LookupError):
    pass


class TriageNotFoundError(LookupError):
    pass


def _output_from_run(run: TriageRun) -> TriageOutput:
    return TriageOutput(
        summary=run.summary,
        hypotheses=json.loads(run.hypotheses_json),
        test_suggestions=json.loads(run.test_suggestions_json),
        limitations=json.loads(run.limitations_json),
    )


def _to_read(run: TriageRun, session: Session) -> TriageRunRead:
    output = _output_from_run(run)
    evidence_ids = json.loads(run.evidence_ids_json)
    chunks = session.scalars(
        select(EvidenceChunk).where(EvidenceChunk.id.in_(evidence_ids))
    ).all() if evidence_ids else []
    score_by_id = {chunk.id: chunk for chunk in chunks}
    evidence = [
        EvidenceChunkRead(
            id=chunk.id,
            source=chunk.source,
            location=chunk.location,
            text=chunk.text,
            score=0.0,
        )
        for evidence_id in evidence_ids
        if (chunk := score_by_id.get(evidence_id)) is not None
    ]
    return TriageRunRead(
        id=run.id,
        report_id=run.report_id,
        mode=run.mode,
        created_at=run.created_at,
        evidence=evidence,
        **output.model_dump(),
    )


def run_triage(
    report_id: int, session: Session, provider: TriageProvider | None = None
) -> TriageRunRead:
    report = session.get(BugReport, report_id)
    if report is None:
        raise ReportNotFoundError(report_id)
    report_read = {
        "id": report.id,
        "title": report.title,
        "description": report.description,
        "expected_behavior": report.expected_behavior,
        "actual_behavior": report.actual_behavior,
        "reproduction_steps": report.reproduction_steps,
        "created_at": report.created_at,
    }
    from ..schemas import BugReportRead

    matches = search_evidence(
        " ".join(
            [
                report.title,
                report.description,
                report.expected_behavior,
                report.actual_behavior,
                report.reproduction_steps or "",
            ]
        ),
        session,
    )
    selected_provider = provider or get_provider()
    output = selected_provider.generate(BugReportRead(**report_read), matches)
    available_ids = {item.id for item in matches}
    unsupported_hypotheses = [item for item in output.hypotheses if not item.evidence_ids]
    if unsupported_hypotheses:
        output = output.model_copy(
            update={
                "hypotheses": [item for item in output.hypotheses if item.evidence_ids],
                "limitations": [
                    *output.limitations,
                    "A cause hypothesis without evidence was omitted.",
                ],
            }
        )
    citations = {
        evidence_id
        for item in [*output.hypotheses, *output.test_suggestions]
        for evidence_id in item.evidence_ids
    }
    if not citations <= available_ids:
        raise ProviderError("Triage referenced evidence that was not supplied for this run.")

    ordered_ids = sorted(citations)
    run = TriageRun(
        report_id=report.id,
        mode=selected_provider.mode,
        summary=output.summary,
        hypotheses_json=json.dumps([item.model_dump() for item in output.hypotheses]),
        test_suggestions_json=json.dumps(
            [item.model_dump() for item in output.test_suggestions]
        ),
        limitations_json=json.dumps(output.limitations),
        evidence_ids_json=json.dumps(ordered_ids),
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return _to_read(run, session)


def list_triage_runs(report_id: int, session: Session) -> list[TriageRunRead]:
    if session.get(BugReport, report_id) is None:
        raise ReportNotFoundError(report_id)
    runs = session.scalars(
        select(TriageRun)
        .where(TriageRun.report_id == report_id)
        .order_by(TriageRun.created_at.desc(), TriageRun.id.desc())
    ).all()
    return [_to_read(run, session) for run in runs]


def save_feedback(
    triage_id: int, payload: FeedbackCreate, session: Session
) -> FeedbackRead:
    if session.get(TriageRun, triage_id) is None:
        raise TriageNotFoundError(triage_id)
    feedback = Feedback(triage_id=triage_id, **payload.model_dump())
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return FeedbackRead.model_validate(feedback)
