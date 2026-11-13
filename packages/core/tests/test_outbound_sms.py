"""Outbound SMS persistence: send bookkeeping and status callbacks (issue #73)."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agent_ant_core.db.models import OutboundMessage, RawEvent
from agent_ant_core.db.outbound_sms import (
    apply_status_callback,
    create_outbound_message,
    find_outbound_for_reply,
    mark_failed,
    mark_sent,
)

NUMBER = "+447000000000"
SID = "SM00000000000000000000000000000001"


def _call(session: Session) -> RawEvent:
    call = RawEvent(
        idempotency_key="CA00000000000000000000000000000001",
        source="voice_call",
        caller_number=NUMBER,
        received_at=datetime.now(),
        payload={},
    )
    session.add(call)
    session.commit()
    return call


def test_create_writes_a_sending_row(session: Session) -> None:
    call = _call(session)
    message = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    session.commit()

    assert message.id is not None
    assert message.status == "sending"
    assert message.twilio_message_sid is None


def test_mark_sent_records_sid_and_timestamp(session: Session) -> None:
    call = _call(session)
    message = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    mark_sent(message, SID)
    session.commit()

    assert message.twilio_message_sid == SID
    assert message.status == "sent"
    assert message.sent_at is not None


def test_mark_failed_records_the_error_code(session: Session) -> None:
    call = _call(session)
    message = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    mark_failed(message, "21211")
    session.commit()

    assert message.status == "failed"
    assert message.error_code == "21211"
    assert message.twilio_message_sid is None


def test_status_callback_updates_by_sid(session: Session) -> None:
    call = _call(session)
    message = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    mark_sent(message, SID)
    session.commit()

    assert apply_status_callback(session, SID, "delivered") is True
    session.commit()
    assert message.status == "delivered"


def test_duplicate_callback_is_idempotent(session: Session) -> None:
    call = _call(session)
    message = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    mark_sent(message, SID)
    session.commit()

    apply_status_callback(session, SID, "delivered")
    session.commit()
    apply_status_callback(session, SID, "delivered")  # at-least-once delivery
    session.commit()

    count = session.execute(select(func.count()).select_from(OutboundMessage)).scalar_one()
    assert count == 1
    assert message.status == "delivered"


def test_unknown_sid_callback_is_ignored(session: Session) -> None:
    assert apply_status_callback(session, "SM-unknown", "delivered") is False


def test_find_outbound_for_reply_links_to_the_triggering_call(session: Session) -> None:
    call = _call(session)
    message = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    session.commit()

    assert find_outbound_for_reply(session, call.id) is message
