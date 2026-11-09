"""Idempotent persistence of extracted job records."""

from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from agent_ant_core.db.models import JobRecord
from agent_ant_core.llm.extraction import JobExtraction


def persist_job_record(
    session: Session,
    *,
    raw_event_id: int,
    idempotency_key: str,
    caller_number: str,
    received_at: datetime,
    raw_message: str,
    job: JobExtraction,
    status: str = "captured",
) -> int | None:
    """Store a job record unless this reply was already extracted.

    Returns the new ``job_records`` id, or ``None`` if a row for this ``idempotency_key`` already
    existed (a retried extraction). Uses ``INSERT ... ON CONFLICT DO NOTHING`` so the database
    decides atomically, exactly as ``persist_raw_event`` does. Trusted fields (``caller_number``,
    ``received_at``) are passed in from the provider event, never taken from the LLM output.
    """

    statement = (
        insert(JobRecord)
        .values(
            raw_event_id=raw_event_id,
            idempotency_key=idempotency_key,
            caller_number=caller_number,
            received_at=received_at,
            raw_message=raw_message,
            name=job.name,
            job_type=job.job_type,
            location=job.location,
            urgency=job.urgency,
            preferred_date=job.preferred_date,
            status=status,
        )
        .on_conflict_do_nothing(index_elements=[JobRecord.idempotency_key])
        .returning(JobRecord.id)
    )
    return session.execute(statement).scalar_one_or_none()
