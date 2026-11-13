"""Persistence of outbound auto-SMS (issue #73).

The send path writes a "sending" row before calling Twilio, then updates it with the SID or the
error, so "did we text this caller, and did it deliver?" is answerable from our own database even
after Twilio's logs are gone. The caller owns the transaction and commits around the network call.
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_core.db.models import OutboundMessage


def create_outbound_message(
    session: Session, *, raw_event_id: int, to: str, body: str
) -> OutboundMessage:
    """Write the pre-send row and return it, flushed so ``id`` is set but not yet committed."""
    row = OutboundMessage(raw_event_id=raw_event_id, to=to, body=body, status="sending")
    session.add(row)
    session.flush()
    return row


def mark_sent(message: OutboundMessage, twilio_sid: str) -> None:
    """Record that Twilio accepted the message and returned a SID."""
    message.twilio_message_sid = twilio_sid
    message.status = "sent"
    message.sent_at = datetime.now(UTC)


def mark_failed(message: OutboundMessage, error_code: str | None) -> None:
    """Record a failed send (Twilio raised, so there is no SID)."""
    message.status = "failed"
    message.error_code = error_code


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
