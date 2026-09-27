from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import BugReport
from ..schemas import BugReportCreate, BugReportRead

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("", response_model=BugReportRead, status_code=status.HTTP_201_CREATED)
def create_report(payload: BugReportCreate, session: Session = Depends(get_session)) -> BugReport:
    report = BugReport(**payload.model_dump())
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


@router.get("", response_model=list[BugReportRead])
def list_reports(session: Session = Depends(get_session)) -> list[BugReport]:
    return list(session.scalars(select(BugReport).order_by(BugReport.created_at.desc(), BugReport.id.desc())))


@router.get("/{report_id}", response_model=BugReportRead)
def get_report(report_id: int, session: Session = Depends(get_session)) -> BugReport:
    report = session.get(BugReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Bug report not found")
    return report
