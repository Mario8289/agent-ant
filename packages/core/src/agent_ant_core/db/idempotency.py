"""Idempotent persistence of raw inbound events."""

from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from agent_ant_core.db.models import EventSource, RawEvent


def persist_raw_event(
    session: Session,
    *,
    idempotency_key: str,
    source: EventSource,
    caller_number: str,
    received_at: datetime,
    payload: dict[str, str],
    related_event_id: int | None = None,
) -> bool:
    """Store the raw event unless this ``idempotency_key`` was already stored.

    Returns ``True`` if a row was inserted and ``False`` if it was a duplicate delivery.

    Uses ``INSERT ... ON CONFLICT DO NOTHING`` so the database decides, atomically. A
    check-then-insert in Python races when two retries land together, and catching the unique
    violation instead would abort the surrounding transaction.

    The caller owns the transaction and must commit before returning 200 to the provider, so
    that "persisted" is true by the time Twilio is told it succeeded. Only a ``True`` result
    should trigger processing; a duplicate must not start a second job or send a second SMS.
    """
    statement = (
        insert(RawEvent)
        .values(
            idempotency_key=idempotency_key,
            source=source,
            caller_number=caller_number,
            received_at=received_at,
            payload=payload,
            related_event_id=related_event_id,
        )
        .on_conflict_do_nothing(index_elements=[RawEvent.idempotency_key])
        .returning(RawEvent.id)
    )
    return session.execute(statement).scalar_one_or_none() is not None
