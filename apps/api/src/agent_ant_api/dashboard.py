"""Human-in-the-loop dashboard: review, approve, edit and reject captured jobs (#28).

One service (D-005), so this lives in the API rather than a separate deployable. The page is
server-rendered (FastAPI + Jinja2) to keep the repo Python-only. Form posts redirect back to the
page; there is no separate JSON API yet. The approval logic is in ``agent_ant_core.db.approval``.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from agent_ant_core.db import approval
from agent_ant_core.db.extraction import list_failed_extractions
from agent_ant_core.db.outbound_sms import list_failed_messages
from agent_ant_core.db.session import get_sessionmaker
from agent_ant_core.metrics import compute_metrics

router = APIRouter()

_TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

URGENCIES = ("unknown", "low", "medium", "high")


def get_session() -> Iterator[Session]:
    with get_sessionmaker()() as session:
        yield session


@router.get("/dashboard")
def dashboard(request: Request, session: Annotated[Session, Depends(get_session)]) -> Response:
    jobs = approval.list_captured_jobs(session)
    metrics = compute_metrics(session)
    failures = list_failed_messages(session)
    failed_extractions = list_failed_extractions(session)
    return _TEMPLATES.TemplateResponse(
        request,
        "dashboard.html",
        {
            "jobs": jobs,
            "metrics": metrics,
            "failures": failures,
            "failed_extractions": failed_extractions,
        },
    )


@router.post("/jobs/{job_id}/approve")
def approve(job_id: int, session: Annotated[Session, Depends(get_session)]) -> RedirectResponse:
    approval.approve_job(session, job_id)
    session.commit()
    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/jobs/{job_id}/reject")
def reject(job_id: int, session: Annotated[Session, Depends(get_session)]) -> RedirectResponse:
    approval.reject_job(session, job_id)
    session.commit()
    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/jobs/{job_id}/edit")
def edit(
    job_id: int,
    session: Annotated[Session, Depends(get_session)],
    name: Annotated[str, Form()] = "",
    job_type: Annotated[str, Form()] = "",
    location: Annotated[str, Form()] = "",
    urgency: Annotated[str, Form()] = "unknown",
    preferred_date: Annotated[str, Form()] = "",
) -> RedirectResponse:
    """Apply corrections and approve. Empty strings mean "clear the field"."""
    edits = {
        "name": name or None,
        "job_type": job_type or None,
        "location": location or None,
        "urgency": urgency if urgency in URGENCIES else "unknown",
        "preferred_date": preferred_date or None,
    }
    approval.edit_job(session, job_id, edits)
    session.commit()
    return RedirectResponse(url="/dashboard", status_code=303)
