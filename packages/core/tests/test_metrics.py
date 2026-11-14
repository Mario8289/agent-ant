"""Business metrics: counts and rates over the funnel (issue #30)."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from agent_ant_core.db.models import (
    HumanEdit,
    JobRecord,
    LLMOutputAudit,
    OutboundMessage,
    RawEvent,
)
from agent_ant_core.metrics import Metrics, compute_metrics

NUMBER = "+447000000000"


def _raw_event(
    session: Session, key: str, source: str, related_event_id: int | None = None
) -> RawEvent:
    row = RawEvent(
        idempotency_key=key,
        source=source,
        caller_number=NUMBER,
        received_at=datetime.now(UTC),
        payload={},
        related_event_id=related_event_id,
    )
    session.add(row)
    session.flush()
    return row


def _outbound(session: Session, raw_event_id: int) -> None:
    session.add(OutboundMessage(raw_event_id=raw_event_id, to=NUMBER, body="hi", status="sent"))


def _job(session: Session, raw_event_id: int, status: str = "captured") -> JobRecord:
    row = JobRecord(
        raw_event_id=raw_event_id,
        idempotency_key=f"J{raw_event_id}",
        caller_number=NUMBER,
        received_at=datetime.now(UTC),
        raw_message="need a tap fixed",
        urgency="unknown",
        status=status,
    )
    session.add(row)
    session.flush()
    return row


def _audit(session: Session, raw_event_id: int, job_id: int) -> LLMOutputAudit:
    row = LLMOutputAudit(
        raw_event_id=raw_event_id,
        job_id=job_id,
        model="m",
        prompt_version="v1",
        raw_output="{}",
        validated=True,
    )
    session.add(row)
    session.flush()
    return row


def test_empty_database_reports_zero_metrics(session: Session) -> None:
    metrics = compute_metrics(session)

    assert metrics == Metrics(0, 0, 0, 0, 0, 0, 0, 0)
    assert metrics.capture_rate == 0.0
    assert metrics.reply_rate == 0.0
    assert metrics.edit_rate == 0.0


def test_full_funnel_counts(session: Session) -> None:
    call = _raw_event(session, "CA1", "voice_call")
    _outbound(session, call.id)
    reply = _raw_event(session, "SM1", "sms_reply", related_event_id=call.id)
    _job(session, reply.id)
    session.commit()

    metrics = compute_metrics(session)

    assert metrics.missed_calls == 1
    assert metrics.jobs == 1
    assert metrics.texts_sent == 1
    assert metrics.replies == 1
    assert metrics.jobs_booked == 0
    assert metrics.edited_jobs == 0
    assert metrics.capture_rate == 1.0
    assert metrics.reply_rate == 1.0
    assert metrics.edit_rate == 0.0


def test_booked_and_edited_are_counted(session: Session) -> None:
    call = _raw_event(session, "CA1", "voice_call")
    _outbound(session, call.id)
    reply = _raw_event(session, "SM1", "sms_reply", related_event_id=call.id)
    job = _job(session, reply.id, status="approved")
    audit = _audit(session, reply.id, job.id)
    session.add(
        HumanEdit(
            llm_output_id=audit.id,
            edit_diff={"job_type": {"before": "x", "after": "y"}},
        )
    )
    session.commit()

    metrics = compute_metrics(session)

    assert metrics.jobs_booked == 1
    assert metrics.edited_jobs == 1
    assert metrics.edit_rate == 1.0


def test_partial_capture_rate(session: Session) -> None:
    _raw_event(session, "CA1", "voice_call")
    _raw_event(session, "CA2", "voice_call")
    reply = _raw_event(session, "SM1", "sms_reply")
    _job(session, reply.id)
    session.commit()

    metrics = compute_metrics(session)

    assert metrics.missed_calls == 2
    assert metrics.jobs == 1
    assert metrics.capture_rate == 0.5


def test_jobs_break_down_by_source(session: Session) -> None:
    sms = _raw_event(session, "SM1", "sms_reply")
    voicemail = _raw_event(session, "RE1", "voicemail")
    _job(session, sms.id)
    _job(session, voicemail.id)
    session.commit()

    metrics = compute_metrics(session)

    assert metrics.jobs == 2
    assert metrics.sms_jobs == 1
    assert metrics.voicemail_jobs == 1


def test_edit_rate_counts_each_job_once(session: Session) -> None:
    call = _raw_event(session, "CA1", "voice_call")
    _outbound(session, call.id)
    reply = _raw_event(session, "SM1", "sms_reply", related_event_id=call.id)
    job = _job(session, reply.id)
    audit = _audit(session, reply.id, job.id)
    session.add(
        HumanEdit(llm_output_id=audit.id, edit_diff={"name": {"before": None, "after": "S"}})
    )
    session.add(
        HumanEdit(llm_output_id=audit.id, edit_diff={"job_type": {"before": "x", "after": "y"}})
    )
    session.commit()

    metrics = compute_metrics(session)

    assert metrics.edited_jobs == 1
