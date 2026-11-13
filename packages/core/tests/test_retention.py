"""Retention and erasure (issue #95): timed redaction and on-request erasure."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from agent_ant_core.db.models import JobRecord, LLMOutputAudit, OutboundMessage, RawEvent
from agent_ant_core.db.retention import erase_person, redact_llm_outputs, redact_raw_events

NUMBER = "+447000000000"
OTHER = "+447111111111"
OLD = datetime.now(UTC) - timedelta(days=91)


def _event(
    session: Session,
    key: str,
    *,
    number: str = NUMBER,
    source: str = "voice_call",
    status: str | None = None,
    created_at: datetime | None = None,
) -> RawEvent:
    row = RawEvent(
        idempotency_key=key,
        source=source,
        caller_number=number,
        received_at=datetime.now(UTC),
        payload={"From": number} if source == "voice_call" else {"Body": "fix a tap"},
        extraction_status=status,
    )
    if created_at is not None:
        row.created_at = created_at
    session.add(row)
    return row


def _audit(
    session: Session, raw_event_id: int, *, created_at: datetime | None = None
) -> LLMOutputAudit:
    row = LLMOutputAudit(
        raw_event_id=raw_event_id,
        model="m",
        prompt_version="v1",
        raw_output='{"name":"Sam"}',
        validated=True,
    )
    if created_at is not None:
        row.created_at = created_at
    session.add(row)
    return row


def test_redact_raw_events_redacts_old_and_protects_retryable(session: Session) -> None:
    old_call = _event(session, "CA1", source="voice_call", created_at=OLD)
    old_done = _event(session, "SM1", source="sms_reply", status="done", created_at=OLD)
    old_dead = _event(session, "SM2", source="sms_reply", status="dead", created_at=OLD)
    old_never = _event(session, "SM3", source="sms_reply", created_at=OLD)  # retryable
    old_failed = _event(session, "SM4", source="sms_reply", status="failed", created_at=OLD)
    fresh_call = _event(session, "CA2", source="voice_call")  # young
    session.commit()

    redacted = redact_raw_events(session)
    session.commit()

    assert redacted == 3
    for row in (old_call, old_done, old_dead):
        session.refresh(row)
        assert row.caller_number == ""
        assert row.payload == {}
    for row in (old_never, old_failed, fresh_call):
        session.refresh(row)
        assert row.caller_number == NUMBER
        assert row.payload != {}


def test_redact_raw_events_is_idempotent(session: Session) -> None:
    _event(session, "CA1", source="voice_call", created_at=OLD)
    session.commit()

    assert redact_raw_events(session) == 1
    session.commit()
    assert redact_raw_events(session) == 0  # already blank


def test_redact_llm_outputs_redacts_old_only(session: Session) -> None:
    old_event = _event(session, "CA1", created_at=OLD)
    fresh_event = _event(session, "CA2")
    session.commit()
    old_audit = _audit(session, old_event.id, created_at=OLD)
    fresh_audit = _audit(session, fresh_event.id)
    session.commit()

    redacted = redact_llm_outputs(session)
    session.commit()

    assert redacted == 1
    session.refresh(old_audit)
    session.refresh(fresh_audit)
    assert old_audit.raw_output == ""
    assert fresh_audit.raw_output == '{"name":"Sam"}'
    assert old_audit.validated is True  # kept


def test_erase_person_clears_that_callers_data_only(session: Session) -> None:
    call = _event(session, "CA1", number=NUMBER, source="voice_call")
    reply = _event(session, "SM1", number=NUMBER, source="sms_reply", status="done")
    session.commit()
    job = JobRecord(
        raw_event_id=reply.id,
        idempotency_key="SM1",
        caller_number=NUMBER,
        received_at=datetime.now(UTC),
        raw_message="Sam needs a tap fixed",
        name="Sam",
        job_type="plumbing",
        location="Leeds",
        urgency="high",
        preferred_date="Monday",
        status="captured",
    )
    session.add(job)
    our_sms = OutboundMessage(raw_event_id=call.id, to=NUMBER, body="hi", status="sent")
    session.add(our_sms)
    our_audit = _audit(session, reply.id)

    other_call = _event(session, "CA9", number=OTHER, source="voice_call")
    other_reply = _event(session, "SM9", number=OTHER, source="sms_reply", status="done")
    session.commit()
    other_job = JobRecord(
        raw_event_id=other_reply.id,
        idempotency_key="SM9",
        caller_number=OTHER,
        received_at=datetime.now(UTC),
        raw_message="other",
        urgency="low",
        status="captured",
    )
    session.add(other_job)
    other_sms = OutboundMessage(raw_event_id=other_call.id, to=OTHER, body="hi", status="sent")
    session.add(other_sms)
    other_audit = _audit(session, other_reply.id)
    session.commit()

    counts = erase_person(session, NUMBER)
    session.commit()

    assert counts == {
        "raw_events": 2,
        "outbound_messages": 1,
        "job_records": 1,
        "llm_output_audits": 1,
    }

    session.refresh(call)
    session.refresh(reply)
    session.refresh(job)
    session.refresh(our_sms)
    session.refresh(our_audit)
    assert call.caller_number == ""
    assert reply.payload == {}
    assert job.caller_number == ""
    assert job.raw_message == ""
    assert job.name is None
    assert job.location is None
    assert job.preferred_date is None
    assert job.job_type == "plumbing"  # operational, kept
    assert job.urgency == "high"
    assert job.status == "captured"
    assert our_audit.raw_output == ""
    assert our_sms.to == ""
    assert our_sms.body == ""

    # another caller is untouched
    session.refresh(other_call)
    session.refresh(other_job)
    session.refresh(other_audit)
    session.refresh(other_sms)
    assert other_call.caller_number == OTHER
    assert other_job.caller_number == OTHER
    assert other_job.raw_message == "other"
    assert other_audit.raw_output == '{"name":"Sam"}'
    assert other_sms.to == OTHER
    assert other_sms.body == "hi"


def test_erase_person_is_idempotent(session: Session) -> None:
    call = _event(session, "CA1", number=NUMBER)
    session.commit()
    session.add(OutboundMessage(raw_event_id=call.id, to=NUMBER, body="hi"))
    session.commit()

    assert erase_person(session, NUMBER)["raw_events"] == 1
    session.commit()
    assert erase_person(session, NUMBER) == {
        "raw_events": 0,
        "outbound_messages": 0,
        "job_records": 0,
        "llm_output_audits": 0,
    }
