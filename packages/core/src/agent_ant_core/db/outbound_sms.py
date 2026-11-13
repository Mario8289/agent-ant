"""Persistence of outbound auto-SMS (issues #73, #34).

The send path writes a "sending" row before calling Twilio, then updates it with the SID or the
error, so "did we text this caller, and did it deliver?" is answerable from our own database even
after Twilio's logs are gone. Failed sends can be retried a bounded number of times and then
dead-lettered (#34). The caller owns the transaction and commits around the network call.
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from agent_ant_core.db.models import OutboundMessage

# A failed send is retried up to this many attempts (including the first), then dead-lettered.
MAX_SEND_ATTEMPTS = 3

# Personal fields (``to``, ``body``) are retained this long, then redacted (D-021).
PERSONAL_RETENTION_DAYS = 30

# A send callable: takes (to, body), returns the Twilio MessageSid, or raises on failure.
SendFn = Callable[[str, str], str]


def create_outbound_message(
    session: Session, *, raw_event_id: int, to: str, body: str
) -> OutboundMessage:
    """Write the pre-send row (first attempt) and return it, flushed so ``id`` is set."""
    row = OutboundMessage(raw_event_id=raw_event_id, to=to, body=body, status="sending")
    session.add(row)
    session.flush()
    return row


def mark_sent(message: OutboundMessage, twilio_sid: str) -> None:
    """Record that Twilio accepted the message and returned a SID."""
    message.twilio_message_sid = twilio_sid
    message.status = "sent"
    message.sent_at = datetime.now(UTC)
    message.error_code = None


def mark_failed(message: OutboundMessage, error_code: str | None) -> None:
    """Record a failed send (Twilio raised, so there is no SID)."""
    message.status = "failed"
    message.error_code = error_code


def retry_failed_sends(
    session: Session, send: SendFn, *, max_attempts: int = MAX_SEND_ATTEMPTS
) -> int:
    """Re-attempt failed sends, dead-lettering those that exhaust their attempts.

    Each failed message whose ``attempts`` is still under ``max_attempts`` is sent again; a
    success records the new SID and clears the error, a failure keeps it ``failed`` and, once the
    bound is reached, moves it to ``dead`` so it can be found and handled by hand. Returns how
    many messages succeeded. The caller commits.
    """
    failed = (
        session.execute(
            select(OutboundMessage)
            .where(
                OutboundMessage.status == "failed",
                OutboundMessage.attempts < max_attempts,
            )
            .order_by(OutboundMessage.created_at.asc())
        )
        .scalars()
        .all()
    )

    succeeded = 0
    for message in failed:
        message.attempts += 1
        try:
            sid = send(message.to, message.body)
        except Exception:
            if message.attempts >= max_attempts:
                message.status = "dead"
            continue
        mark_sent(message, sid)
        succeeded += 1
    return succeeded


def list_failed_messages(session: Session, *, limit: int = 20) -> list[OutboundMessage]:
    """Recent failed or dead sends, for the dashboard's failure panel."""
    return list(
        session.execute(
            select(OutboundMessage)
            .where(OutboundMessage.status.in_(("failed", "dead")))
            .order_by(OutboundMessage.created_at.desc())
            .limit(limit)
        ).scalars()
    )


def apply_status_callback(
    session: Session, twilio_sid: str, status: str, error_code: str | None = None
) -> bool:
    """Update a message's status from a Twilio status callback, idempotently.

    Returns ``True`` if a row matched and ``False`` if the SID is unknown (e.g. a message sent
    before this table existed). A duplicate callback simply sets the same status again; it does
    not create a row, so "at least once" callback delivery is safe.
    """
    message = session.execute(
        select(OutboundMessage).where(OutboundMessage.twilio_message_sid == twilio_sid)
    ).scalar_one_or_none()
    if message is None:
        return False
    message.status = status
    if error_code is not None:
        message.error_code = error_code
    return True


def find_outbound_for_reply(session: Session, related_event_id: int) -> OutboundMessage | None:
    """The auto-text a reply answers: the outbound message triggered by that missed call.

    A reply is linked to its missed call by ``raw_events.related_event_id``, and the auto-text is
    linked to the same call by ``outbound_messages.raw_event_id`` — so this is the join that turns
    "replied to that number" into "replied to that specific text".
    """
    return session.execute(
        select(OutboundMessage)
        .where(OutboundMessage.raw_event_id == related_event_id)
        .order_by(OutboundMessage.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()


def purge_personal_data(
    session: Session, *, older_than: timedelta = timedelta(days=PERSONAL_RETENTION_DAYS)
) -> int:
    """Redact the personal fields of outbound messages past the retention window (D-021).

    ``to`` and ``body`` are cleared (set to ``""``); the SID, status, error code and timestamps
    stay so aggregate metrics remain correct. Only rows that still hold data are touched, so the
    purge is idempotent. Returns the number of rows redacted. The caller commits.
    """
    cutoff = datetime.now(UTC) - older_than
    updated_ids = session.scalars(
        update(OutboundMessage)
        .where(
            OutboundMessage.created_at < cutoff,
            OutboundMessage.to != "",
            OutboundMessage.body != "",
        )
        .values(to="", body="")
        .returning(OutboundMessage.id)
    ).all()
    return len(updated_ids)
