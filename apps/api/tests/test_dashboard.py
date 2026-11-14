"""Tests for the HITL dashboard endpoints (#28)."""

from collections.abc import Callable, Iterator
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_api.dashboard import get_session as dashboard_get_session
from agent_ant_api.main import create_app
from agent_ant_core.audit.records import record_llm_output
from agent_ant_core.db.idempotency import persist_raw_event
from agent_ant_core.db.jobs import persist_job_record
from agent_ant_core.db.models import HumanEdit, JobRecord, RawEvent
from agent_ant_core.llm import JobExtraction

MESSAGE_SID = "SM00000000000000000000000000000001"
CALLER = "+447000000000"


def _use(session: Session) -> Callable[[], Iterator[Session]]:
    def dependency() -> Iterator[Session]:
        yield session

    return dependency


def _client(session: Session) -> TestClient:
    app = create_app()
    app.dependency_overrides[dashboard_get_session] = _use(session)
    return TestClient(app)


def _captured_job(session: Session) -> int:
    persist_raw_event(
        session,
        idempotency_key=MESSAGE_SID,
        source="sms_reply",
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        payload={"MessageSid": MESSAGE_SID, "Body": "need a wardrobe fitted"},
    )
    session.flush()
    event_id = session.execute(select(RawEvent.id)).scalar_one()

    job_id = persist_job_record(
        session,
        raw_event_id=event_id,
        idempotency_key=MESSAGE_SID,
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        raw_message="need a wardrobe fitted",
        job=JobExtraction(
            name="Sam", job_type="wardrobe fitting", location="Leeds", urgency="high"
        ),
    )
    assert job_id is not None
    record_llm_output(
        session,
        raw_event_id=event_id,
        job_id=job_id,
        model="test-model",
        prompt_version="extract_v1",
        raw_output="{}",
        validated=True,
    )
    session.commit()
    return job_id


def test_dashboard_lists_captured_jobs(session: Session) -> None:
    _captured_job(session)
    response = _client(session).get("/dashboard")

    assert response.status_code == 200
    assert "need a wardrobe fitted" in response.text
    assert "wardrobe fitting" in response.text


def test_failed_extraction_shows_the_reply_body(session: Session) -> None:
    persist_raw_event(
        session,
        idempotency_key="SM-dead",
        source="sms_reply",
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        payload={"Body": "burst pipe under the sink"},
    )
    reply = session.execute(
        select(RawEvent).where(RawEvent.idempotency_key == "SM-dead")
    ).scalar_one()
    reply.extraction_status = "dead"
    reply.extraction_attempts = 3
    session.commit()

    response = _client(session).get("/dashboard")

    assert response.status_code == 200
    assert "burst pipe under the sink" in response.text


def test_approve_endpoint_approves(session: Session) -> None:
    job_id = _captured_job(session)
    response = _client(session).post(f"/jobs/{job_id}/approve", follow_redirects=False)

    assert response.status_code == 303
    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.status == "approved"


def test_reject_endpoint_rejects(session: Session) -> None:
    job_id = _captured_job(session)
    response = _client(session).post(f"/jobs/{job_id}/reject", follow_redirects=False)

    assert response.status_code == 303
    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.status == "rejected"


def test_edit_endpoint_applies_changes_and_writes_an_edit(session: Session) -> None:
    job_id = _captured_job(session)
    response = _client(session).post(
        f"/jobs/{job_id}/edit",
        data={
            "name": "Sam",
            "job_type": "wardrobe doors",
            "location": "Leeds",
            "urgency": "medium",
            "preferred_date": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.job_type == "wardrobe doors"
    assert job.urgency == "medium"
    assert job.status == "approved"

    edit = session.execute(select(HumanEdit)).scalar_one()
    assert edit.edit_diff["job_type"] == {"before": "wardrobe fitting", "after": "wardrobe doors"}
