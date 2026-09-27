from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_session
from ..schemas import FeedbackCreate, FeedbackRead, TriageRunRead
from ..services.providers import get_provider
from ..services.providers.base import ProviderError, TriageProvider
from ..services.triage import (
    ReportNotFoundError,
    TriageNotFoundError,
    list_triage_runs,
    run_triage,
    save_feedback,
)

router = APIRouter(tags=["triage"])


@router.post(
    "/api/reports/{report_id}/triage",
    response_model=TriageRunRead,
    status_code=status.HTTP_200_OK,
)
def create_triage(
    report_id: int,
    session: Session = Depends(get_session),
    provider: TriageProvider = Depends(get_provider),
) -> TriageRunRead:
    try:
        return run_triage(report_id, session, provider)
    except ReportNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Bug report not found") from exc
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/api/reports/{report_id}/triage", response_model=list[TriageRunRead])
def get_triage_history(
    report_id: int, session: Session = Depends(get_session)
) -> list[TriageRunRead]:
    try:
        return list_triage_runs(report_id, session)
    except ReportNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Bug report not found") from exc


@router.post(
    "/api/triage/{triage_id}/feedback",
    response_model=FeedbackRead,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback(
    triage_id: int,
    payload: FeedbackCreate,
    session: Session = Depends(get_session),
) -> FeedbackRead:
    try:
        return save_feedback(triage_id, payload, session)
    except TriageNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Triage run not found") from exc
