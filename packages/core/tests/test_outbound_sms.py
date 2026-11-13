"""Outbound SMS persistence: send bookkeeping and status callbacks (issue #73)."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agent_ant_core.db.models import OutboundMessage, RawEvent
from agent_ant_core.db.outbound_sms import (
    apply_status_callback,
    create_outbound_message,
    find_outbound_for_reply,
    list_failed_messages,
    mark_failed,
    mark_sent,
    purge_personal_data,
    retry_failed_sends,
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


# --- retry and dead-letter (issue #34) -----------------------------------------------------


class _Sender:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls = 0

    def __call__(self, to: str, body: str) -> str:
        self.calls += 1
        if self.error:
            raise self.error
        return "SMretried"


def _failed(session: Session, attempts: int = 1) -> OutboundMessage:
    call = _call(session)
    message = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    message.status = "failed"
    message.attempts = attempts
    message.error_code = "21211"
    session.commit()
    return message


def test_retry_failed_sends_resends_and_records_success(session: Session) -> None:
    message = _failed(session)
    sender = _Sender()

    assert retry_failed_sends(session, sender) == 1
    session.commit()

    assert message.status == "sent"
    assert message.attempts == 2
    assert message.twilio_message_sid == "SMretried"
    assert message.error_code is None


def test_retry_dead_letters_after_max_attempts(session: Session) -> None:
    message = _failed(session, attempts=2)  # one attempt left under the default bound of 3
    sender = _Sender(error=RuntimeError("twilio is down"))

    assert retry_failed_sends(session, sender) == 0
    session.commit()

    assert message.status == "dead"
    assert message.attempts == 3


def test_retry_invokes_on_dead_letter_per_dead_message(session: Session) -> None:
    message = _failed(session, attempts=2)
    sender = _Sender(error=RuntimeError("twilio is down"))
    dead: list[OutboundMessage] = []

    assert retry_failed_sends(session, sender, on_dead_letter=dead.append) == 0
    session.commit()

    assert dead == [message]
    assert message.status == "dead"


def test_retry_does_not_invoke_on_dead_letter_on_success(session: Session) -> None:
    message = _failed(session)  # attempts=1, the retry succeeds
    sender = _Sender()
    dead: list[OutboundMessage] = []

    assert retry_failed_sends(session, sender, on_dead_letter=dead.append) == 1
    session.commit()

    assert dead == []
    assert message.status == "sent"


def test_retry_skips_messages_already_at_the_bound(session: Session) -> None:
    message = _failed(session, attempts=3)  # already exhausted
    sender = _Sender()

    assert retry_failed_sends(session, sender) == 0
    session.commit()

    assert message.attempts == 3  # untouched
    assert sender.calls == 0


def test_list_failed_messages_returns_failed_and_dead(session: Session) -> None:
    call = _call(session)
    failed = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    failed.status = "failed"
    dead = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    dead.status = "dead"
    sent = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    mark_sent(sent, "SMsent")
    session.commit()

    messages = list_failed_messages(session)

    assert {m.id for m in messages} == {failed.id, dead.id}


def test_purge_personal_data_redacts_only_old_messages(session: Session) -> None:
    call = _call(session)
    old = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    old.created_at = datetime.now(UTC) - timedelta(days=31)
    fresh = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    session.commit()

    purged = purge_personal_data(session)
    session.commit()

    assert purged == 1
    session.refresh(old)
    session.refresh(fresh)
    assert old.to == ""
    assert old.body == ""
    assert fresh.to == NUMBER
    assert fresh.body == "hi"


def test_purge_is_idempotent(session: Session) -> None:
    call = _call(session)
    old = create_outbound_message(session, raw_event_id=call.id, to=NUMBER, body="hi")
    old.created_at = datetime.now(UTC) - timedelta(days=31)
    session.commit()

    assert purge_personal_data(session) == 1
    session.commit()
    assert purge_personal_data(session) == 0  # nothing left to redact
