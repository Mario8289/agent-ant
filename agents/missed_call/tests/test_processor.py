"""Tests for ``process_reply``: extraction plus persistence (Week 2 integration)."""

import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_core.db.idempotency import persist_raw_event
from agent_ant_core.db.models import JobRecord, LLMOutputAudit, RawEvent
from agent_ant_core.testing import FakeLLM
from agent_ant_missed_call.processor import process_reply

MESSAGE_SID = "SM00000000000000000000000000000001"
CALLER = "+447000000000"
MESSAGE = "need a wardrobe fitted in Leeds"
GOOD = json.dumps(
    {"name": "Sam", "job_type": "wardrobe fitting", "location": "Leeds", "urgency": "high"}
)


def _reply_id(session: Session) -> int:
    persist_raw_event(
        session,
        idempotency_key=MESSAGE_SID,
        source="sms_reply",
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        payload={"MessageSid": MESSAGE_SID, "Body": MESSAGE},
    )
    session.flush()
    return session.execute(select(RawEvent.id)).scalar_one()


def _process(session: Session, llm: FakeLLM, event_id: int) -> int | None:
    return process_reply(
        session,
        llm,
        raw_event_id=event_id,
        idempotency_key=MESSAGE_SID,
        caller_number=CALLER,
        received_at=datetime.now(UTC),
        message=MESSAGE,
        model="test-model",
    )


def test_valid_reply_becomes_a_captured_job_and_audit_row(session: Session) -> None:
    event_id = _reply_id(session)
    job_id = _process(session, FakeLLM(GOOD), event_id)
    session.commit()

    assert job_id is not None
    job = session.execute(select(JobRecord)).scalar_one()
    assert job.status == "captured"
    assert job.job_type == "wardrobe fitting"
    assert job.caller_number == CALLER

    audit = session.execute(select(LLMOutputAudit)).scalar_one()
    assert audit.job_id == job_id
    assert audit.raw_event_id == event_id
    assert audit.validated is True
    assert audit.model == "test-model"
    assert audit.prompt_version == "extract_v3"


def test_invalid_reply_writes_an_audit_row_but_no_job(session: Session) -> None:
    event_id = _reply_id(session)
    # The fake never recovers, so repair is exhausted and no job is written.
    job_id = _process(session, FakeLLM(*["not json"] * 10), event_id)
    session.commit()

    assert job_id is None
    assert session.execute(select(JobRecord)).scalars().all() == []
    audit = session.execute(select(LLMOutputAudit)).scalar_one()
    assert audit.validated is False
    assert audit.job_id is None
    assert audit.repair_attempts == 2
