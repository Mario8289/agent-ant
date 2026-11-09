"""Tests for job-record persistence (Week 2 integration)."""

from datetime import UTC, datetime

from sqlalchemy import Engine, inspect, select
from sqlalchemy.orm import Session

from agent_ant_core.db.idempotency import persist_raw_event
from agent_ant_core.db.jobs import persist_job_record
from agent_ant_core.db.models import JobRecord, RawEvent
from agent_ant_core.llm import JobExtraction

MESSAGE_SID = "SM00000000000000000000000000000001"
CALLER = "+447000000000"


def _reply_id(session: Session) -> int:
    persist_raw_event(
        session,
        idempotency_key=MESSAGE_SID,
        source="sms_reply",
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        payload={"MessageSid": MESSAGE_SID, "Body": "need a wardrobe fitted"},
    )
    session.flush()
    return session.execute(select(RawEvent.id)).scalar_one()


def _job() -> JobExtraction:
    return JobExtraction(name="Sam", job_type="wardrobe fitting", location="Leeds", urgency="high")


def _persist(session: Session, event_id: int) -> int | None:
    return persist_job_record(
        session,
        raw_event_id=event_id,
        idempotency_key=MESSAGE_SID,
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        raw_message="need a wardrobe fitted",
        job=_job(),
    )


def test_migration_creates_job_records_with_a_unique_key(engine: Engine) -> None:
    constraints = inspect(engine).get_unique_constraints("job_records")
    assert [c["column_names"] for c in constraints] == [["idempotency_key"]]


def test_job_record_stores_trusted_and_extracted_fields(session: Session) -> None:
    event_id = _reply_id(session)
    job_id = _persist(session, event_id)
    session.commit()

    row = session.execute(select(JobRecord)).scalar_one()
    assert row.id == job_id
    assert row.raw_event_id == event_id
    assert row.caller_number == CALLER
    assert row.raw_message == "need a wardrobe fitted"
    assert row.name == "Sam"
    assert row.job_type == "wardrobe fitting"
    assert row.urgency == "high"
    assert row.status == "captured"
    assert row.received_at.tzinfo is not None


def test_duplicate_job_record_is_a_no_op(session: Session) -> None:
    event_id = _reply_id(session)
    assert _persist(session, event_id) is not None
    assert _persist(session, event_id) is None
    session.commit()

    assert len(session.execute(select(JobRecord)).scalars().all()) == 1
