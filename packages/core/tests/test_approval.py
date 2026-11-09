"""Tests for the human-approval logic (HITL, rule 6)."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_core.audit.records import record_llm_output
from agent_ant_core.db.approval import approve_job, edit_job, list_captured_jobs, reject_job
from agent_ant_core.db.idempotency import persist_raw_event
from agent_ant_core.db.jobs import persist_job_record
from agent_ant_core.db.models import HumanEdit, JobRecord, RawEvent
from agent_ant_core.llm import JobExtraction

MESSAGE_SID = "SM00000000000000000000000000000001"
CALLER = "+447000000000"


def _captured_job(session: Session) -> int:
    """Persist a reply, its extracted job and its audit row; return the job id."""
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
    session.flush()
    return job_id


def test_list_captured_jobs_returns_only_captured(session: Session) -> None:
    job_id = _captured_job(session)
    session.commit()
    assert [j.id for j in list_captured_jobs(session)] == [job_id]

    approve_job(session, job_id)
    session.commit()
    assert list_captured_jobs(session) == []


def test_approve_moves_a_captured_job_to_approved(session: Session) -> None:
    job_id = _captured_job(session)
    assert approve_job(session, job_id) is not None
    session.commit()
    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.status == "approved"


def test_reject_moves_a_captured_job_to_rejected(session: Session) -> None:
    job_id = _captured_job(session)
    reject_job(session, job_id)
    session.commit()
    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.status == "rejected"


def test_edit_applies_changes_and_approves(session: Session) -> None:
    job_id = _captured_job(session)
    edit_job(session, job_id, {"job_type": "wardrobe doors", "urgency": "medium"})
    session.commit()

    job = session.get(JobRecord, job_id)
    assert job is not None
    assert job.job_type == "wardrobe doors"
    assert job.urgency == "medium"
    assert job.status == "approved"


def test_edit_writes_a_human_edit_with_the_diff(session: Session) -> None:
    job_id = _captured_job(session)
    edit_job(session, job_id, {"job_type": "wardrobe doors"})
    session.commit()

    edit = session.execute(select(HumanEdit)).scalar_one()
    assert edit.edit_diff == {"job_type": {"before": "wardrobe fitting", "after": "wardrobe doors"}}


def test_edit_ignores_unchanged_fields(session: Session) -> None:
    job_id = _captured_job(session)
    edit_job(session, job_id, {"job_type": "wardrobe fitting"})  # unchanged
    session.commit()
    assert session.execute(select(HumanEdit)).scalars().all() == []


def test_approve_an_already_decided_job_returns_none(session: Session) -> None:
    job_id = _captured_job(session)
    approve_job(session, job_id)
    session.commit()
    assert approve_job(session, job_id) is None
