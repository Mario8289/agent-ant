"""Retention and erasure of personal data (issue #95, D-027).

Two distinct jobs, run by scripts rather than the request path:

- **Time-based redaction.** ``raw_events.payload`` / ``raw_events.caller_number`` and
  ``llm_output_audits.raw_output`` hold caller numbers and message text. They are kept 90 days
  and then blanked, which is long enough to replay a failed extraction and to debug, and short
  enough to be defensible. ``job_records`` and ``human_edits`` are *not* touched: they are the
  tradesperson's own business record (the product), so a blanket purge would destroy the history
  of work done.
- **Erasure on request.** ``erase_person`` removes one caller's personal data across every table,
  for a right-to-erasure request. The caller's raw input and identifying fields go; the
  operational skeleton (status, timestamps, job type, urgency) stays so counts and metrics stay
  coherent.

Redaction is *blanking*, not deleting: the idempotency key, ``source``, timestamps, status and
attempt counts all survive, so a late Twilio retry still cannot create a duplicate and the
metrics (which count rows by ``source``, never by number) are unaffected.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, not_, or_, select, update
from sqlalchemy.orm import Session

from agent_ant_core.db.extraction import FAILED
from agent_ant_core.db.models import JobRecord, LLMOutputAudit, OutboundMessage, RawEvent

# Raw inbound payloads and the number inside them are retained this long, then redacted (D-027).
RAW_RETENTION_DAYS = 90

# A job's extracted name/location/preferred date are identifying, so erasure clears them; the
# operational fields (job_type, urgency, status) are not identifying and are kept.
_ERASED_JOB_FIELDS = {
    "caller_number": "",
    "raw_message": "",
    "name": None,
    "location": None,
    "preferred_date": None,
}


def redact_raw_events(
    session: Session, *, older_than: timedelta = timedelta(days=RAW_RETENTION_DAYS)
) -> int:
    """Blank ``raw_events.payload`` and ``caller_number`` past the retention window.

    A reply that is still retryable — extraction never ran (``status`` NULL) or last failed —
    is skipped: blanking its body would turn a recoverable lead into an empty, guaranteed
    dead-letter when ``retry_failed_extractions`` next runs. Voice calls (never extracted) and
    done/dead replies are redacted. Idempotent: rows whose number is already blank are skipped.
    Returns the number of rows redacted. The caller commits.
    """
    cutoff = datetime.now(UTC) - older_than
    retryable = and_(
        RawEvent.source == "sms_reply",
        or_(RawEvent.extraction_status.is_(None), RawEvent.extraction_status == FAILED),
    )
    ids = session.scalars(
        update(RawEvent)
        .where(
            RawEvent.created_at < cutoff,
            RawEvent.caller_number != "",
            not_(retryable),
        )
        .values(caller_number="", payload={})
        .returning(RawEvent.id)
    ).all()
    return len(ids)


def redact_llm_outputs(
    session: Session, *, older_than: timedelta = timedelta(days=RAW_RETENTION_DAYS)
) -> int:
    """Blank ``llm_output_audits.raw_output`` past the retention window (D-027).

    The model's raw text is derived from the caller's words, so it is redacted on the same 90-day
    schedule. ``validated``, ``repair_attempts``, ``model`` and ``prompt_version`` stay, so the
    edit-rate and drift signals are unaffected. ``job_records`` and ``human_edits`` are exempt.
    Idempotent. Returns the number of rows redacted. The caller commits.
    """
    cutoff = datetime.now(UTC) - older_than
    ids = session.scalars(
        update(LLMOutputAudit)
        .where(LLMOutputAudit.created_at < cutoff, LLMOutputAudit.raw_output != "")
        .values(raw_output="")
        .returning(LLMOutputAudit.id)
    ).all()
    return len(ids)


def erase_person(session: Session, caller_number: str) -> dict[str, int]:
    """Remove one caller's personal data across every table, for a right-to-erasure request.

    Clears the caller's number and message text from ``raw_events`` and ``outbound_messages``,
    their raw message and identifying extracted fields from ``job_records``, and the derived raw
    output from ``llm_output_audits`` (joined through ``raw_event_id``). The operational skeleton
    stays so counts and metrics remain coherent, and another caller's rows are never touched.
    ``human_edits`` — the tradesperson's own corrections — is the operator's action trail and is
    intentionally left alone. Idempotent. Returns a per-table count of rows redacted. The caller
    commits.
    """
    # Capture the caller's raw event ids before redacting them, so the audit join still resolves.
    raw_event_ids = session.scalars(
        select(RawEvent.id).where(RawEvent.caller_number == caller_number)
    ).all()

    raw = len(
        session.scalars(
            update(RawEvent)
            .where(RawEvent.caller_number == caller_number, RawEvent.caller_number != "")
            .values(caller_number="", payload={})
            .returning(RawEvent.id)
        ).all()
    )
    outbound = len(
        session.scalars(
            update(OutboundMessage)
            .where(OutboundMessage.to == caller_number)
            .values(to="", body="")
            .returning(OutboundMessage.id)
        ).all()
    )
    jobs = len(
        session.scalars(
            update(JobRecord)
            .where(JobRecord.caller_number == caller_number)
            .values(**_ERASED_JOB_FIELDS)
            .returning(JobRecord.id)
        ).all()
    )
    audits = len(
        session.scalars(
            update(LLMOutputAudit)
            .where(
                LLMOutputAudit.raw_event_id.in_(raw_event_ids),
                LLMOutputAudit.raw_output != "",
            )
            .values(raw_output="")
            .returning(LLMOutputAudit.id)
        ).all()
    )
    return {
        "raw_events": raw,
        "outbound_messages": outbound,
        "job_records": jobs,
        "llm_output_audits": audits,
    }
