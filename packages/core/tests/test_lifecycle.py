"""Tests for the four-state job lifecycle (D-030)."""

import itertools
from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_core.db.idempotency import persist_raw_event
from agent_ant_core.db.jobs import persist_job_record
from agent_ant_core.db.lifecycle import ALLOWED_TRANSITIONS, set_on_hold, transition
from agent_ant_core.db.models import JobEvent, JobRecord, RawEvent
from agent_ant_core.llm import JobExtraction

CALLER = "+447000000000"
ALL_STATUSES = ["enquiry", "in_progress", "completed", "lost"]

_counter = itertools.count()


def _job(session: Session, status: str) -> int:
    """Create a job already sitting in ``status`` (test setup, not a real transition)."""
    n = next(_counter)
    persist_raw_event(
        session,
        idempotency_key=f"CA{n}",
        source="voice_call",
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        payload={},
    )
    session.flush()
    event_id = session.execute(select(RawEvent.id)).scalar_one()
    job = JobRecord(
        raw_event_id=event_id,
        idempotency_key=f"JOB{n}",
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        raw_message="",
        job_status=status,
    )
    session.add(job)
    session.flush()
    return job.id


@pytest.mark.parametrize("from_status", ALL_STATUSES)
@pytest.mark.parametrize("to_status", ALL_STATUSES)
def test_transition_respects_the_allowed_table(
    session: Session, from_status: str, to_status: str
) -> None:
    job_id = _job(session, from_status)
    allowed = to_status in ALLOWED_TRANSITIONS[from_status]

    result = transition(session, job_id, to_status, actor="trader", reason="test")

    assert (result is not None) is allowed
    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.job_status == (to_status if allowed else from_status)
    events = session.execute(select(JobEvent).where(JobEvent.job_id == job_id)).scalars().all()
    assert len(events) == (1 if allowed else 0)


def test_allowed_transition_writes_the_event_fields(session: Session) -> None:
    job_id = _job(session, "enquiry")
    transition(session, job_id, "in_progress", actor="trader", reason="quote sent")
    session.commit()

    event = session.execute(select(JobEvent)).scalar_one()
    assert (event.from_status, event.to_status, event.actor, event.reason) == (
        "enquiry",
        "in_progress",
        "trader",
        "quote sent",
    )
    assert event.created_at is not None


def test_transition_clears_on_hold_when_leaving_in_progress(session: Session) -> None:
    job_id = _job(session, "in_progress")
    assert set_on_hold(session, job_id, True) is not None
    session.commit()
    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.on_hold is True

    transition(session, job_id, "completed", actor="trader")
    session.commit()
    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.on_hold is False


def test_on_hold_can_only_be_set_on_in_progress(session: Session) -> None:
    job_id = _job(session, "enquiry")
    assert set_on_hold(session, job_id, True) is None
    session.commit()
    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.on_hold is False


def test_missing_job_transition_returns_none(session: Session) -> None:
    assert transition(session, 999999, "in_progress", actor="trader") is None


def test_persisted_job_defaults_to_enquiry(session: Session) -> None:
    persist_raw_event(
        session,
        idempotency_key="SM-default",
        source="sms_reply",
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        payload={"MessageSid": "SM-default", "Body": "need a wardrobe fitted"},
    )
    session.flush()
    event_id = session.execute(select(RawEvent.id)).scalar_one()
    job_id = persist_job_record(
        session,
        raw_event_id=event_id,
        idempotency_key="SM-default",
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        raw_message="need a wardrobe fitted",
        job=JobExtraction(
            name="Sam", job_type="wardrobe fitting", location="Leeds", urgency="high"
        ),
    )
    assert job_id is not None
    session.commit()

    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.job_status == "enquiry"
    assert job.on_hold is False
