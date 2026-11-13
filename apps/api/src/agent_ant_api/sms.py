"""Fixed-template auto-SMS to the caller of a missed call.

The text is a fixed template with the business name filled in. The AI never writes free text to
customers (D-004), so nothing here takes model output. It runs as a background task after the
webhook has already stored the event and answered Twilio, so a slow or failing send can never
delay or fail the webhook.
"""

import logging
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from twilio.base.exceptions import TwilioRestException
from twilio.http.http_client import TwilioHttpClient
from twilio.rest import Client

from agent_ant_core.config import Settings, get_settings
from agent_ant_core.db.models import RawEvent
from agent_ant_core.db.outbound_sms import create_outbound_message, mark_failed, mark_sent

logger = logging.getLogger(__name__)

# Seconds. Twilio's client has no timeout by default, so a stalled connection would pin a
# worker thread forever.
SEND_TIMEOUT = 10

# Opening line is skipped when no business name is configured. The wording explains why the
# text comes from an unfamiliar number and asks for a reply (R2, D-011). Kept short: over 160
# characters an SMS is split into segments and billed per segment.
TEMPLATE_WITH_NAME = (
    "Hi, it's {business_name}. Sorry we missed your call. This is our text line: reply with "
    "your name, the job and where, and we'll get back to you."
)
TEMPLATE_WITHOUT_NAME = (
    "Sorry we missed your call. This is our text line: reply with your name, the job and "
    "where, and we'll get back to you."
)

# Opt-out and help keywords (#72, D-019). These are the keywords Twilio itself recognises, plus
# the variants callers actually send. The body is normalised before matching, so " stop " and
# "STOP" both count; a normal reply like "help fix the tap" does not, because only the exact
# keyword matches.
STOP_KEYWORDS = frozenset({"STOP", "STOPALL", "UNSUBSCRIBE", "CANCEL", "END", "QUIT"})
HELP_KEYWORDS = frozenset({"HELP"})

# Two more fixed templates (D-004: the AI never writes free text). A STOP is confirmed so the
# caller knows it worked; a HELP gets the same "reply with name/job/where" instruction as the
# missed-call text, plus the number to call back.
STOP_CONFIRM_WITH_NAME = (
    "You won't get more texts from {business_name}. Call us if you need anything."
)
STOP_CONFIRM_WITHOUT_NAME = "You won't get more texts from us. Call us if you need anything."
HELP_WITH_NAME = (
    "This is {business_name}'s text line. Reply with your name, the job and where, and we'll "
    "get back to you."
)
HELP_WITHOUT_NAME = (
    "This is our text line. Reply with your name, the job and where, and we'll get back to you."
)

# Sends one text and returns the Twilio MessageSid. None when Twilio is not configured.
SmsSender = Callable[[str, str], str]

# A callable that hands out a fresh session, so a background send can persist its own row.
SessionFactory = Callable[[], Session]


def build_missed_call_message(business_name: str | None) -> str:
    if business_name:
        return TEMPLATE_WITH_NAME.format(business_name=business_name)
    return TEMPLATE_WITHOUT_NAME


def _normalise_keyword(body: str) -> str:
    return body.strip().upper()


def is_stop_keyword(body: str) -> bool:
    """True when the reply is an opt-out (STOP or a recognised variant), ignoring case/space."""
    return _normalise_keyword(body) in STOP_KEYWORDS


def is_help_keyword(body: str) -> bool:
    """True when the reply asks for help, ignoring case/space."""
    return _normalise_keyword(body) in HELP_KEYWORDS


def build_stop_confirmation(business_name: str | None) -> str:
    if business_name:
        return STOP_CONFIRM_WITH_NAME.format(business_name=business_name)
    return STOP_CONFIRM_WITHOUT_NAME


def build_help_reply(business_name: str | None) -> str:
    if business_name:
        return HELP_WITH_NAME.format(business_name=business_name)
    return HELP_WITHOUT_NAME


def get_sms_sender(settings: Annotated[Settings, Depends(get_settings)]) -> SmsSender | None:
    """A Twilio-backed sender, or None if account, token or from-number is missing.

    Returns the Twilio MessageSid so the caller can persist it. If a public base URL is set, each
    message carries a ``status_callback`` back to this app so delivery status can be recorded
    (#73); without it, sends still work but status stays ``sent``.
    """
    if not (
        settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_from_number
    ):
        return None

    client = Client(
        settings.twilio_account_sid,
        settings.twilio_auth_token.get_secret_value(),
        http_client=TwilioHttpClient(timeout=SEND_TIMEOUT),
    )
    from_number = settings.twilio_from_number
    status_callback = (
        f"{settings.public_base_url.rstrip('/')}/webhooks/sms-status"
        if settings.public_base_url
        else None
    )

    def send(to: str, body: str) -> str:
        kwargs: dict[str, str] = {"to": to, "from_": from_number, "body": body}
        if status_callback:
            kwargs["status_callback"] = status_callback
        message = client.messages.create(**kwargs)
        # A successful create always carries a SID; the stub types it optional.
        sid = message.sid
        assert sid is not None
        return sid

    return send


def _lookup_raw_event_id(session: Session, idempotency_key: str) -> int | None:
    return session.execute(
        select(RawEvent.id).where(RawEvent.idempotency_key == idempotency_key)
    ).scalar_one_or_none()


def _error_code(exc: Exception) -> str | None:
    """The Twilio error code (e.g. ``21211``) when the exception carries one, else None."""
    if isinstance(exc, TwilioRestException):
        return str(exc.code)
    return None


def _send_and_persist(
    sender: SmsSender | None,
    make_session: SessionFactory,
    *,
    trigger_sid: str,
    to: str,
    body: str,
) -> None:
    """Send one text and record the outcome in ``outbound_messages``. Never raises.

    The row is written and committed *before* the Twilio call (the outbound analogue of
    persist-before-processing), then updated with the SID or the error. The webhook has already
    answered Twilio by the time this runs, so a failure here is logged, not re-thrown. There is
    no retry or outbox yet (#34); a failed send is recorded but not retried.
    """
    with make_session() as session:
        raw_event_id = _lookup_raw_event_id(session, trigger_sid)
        if raw_event_id is None:
            logger.warning("%s: raw event missing, no sms recorded", trigger_sid)
            return
        message = create_outbound_message(session, raw_event_id=raw_event_id, to=to, body=body)
        session.commit()

        if sender is None:
            mark_failed(message, "unconfigured")
            session.commit()
            logger.warning("%s: twilio is not configured, no sms sent", trigger_sid)
            return

        try:
            twilio_sid = sender(to, body)
        except Exception as exc:
            # Broad on purpose: Twilio API errors and network timeouts are different exception
            # types, and none of them may escape a background task.
            mark_failed(message, _error_code(exc))
            session.commit()
            logger.exception("%s: sms send failed", trigger_sid)
            return

        mark_sent(message, twilio_sid)
        session.commit()


def send_missed_call_sms(
    sender: SmsSender | None,
    business_name: str | None,
    call_sid: str,
    to: str,
    make_session: SessionFactory,
) -> None:
    """Send the missed-call template text and persist the outbound message."""
    _send_and_persist(
        sender,
        make_session,
        trigger_sid=call_sid,
        to=to,
        body=build_missed_call_message(business_name),
    )


def send_stop_confirmation(
    sender: SmsSender | None,
    business_name: str | None,
    message_sid: str,
    to: str,
    make_session: SessionFactory,
) -> None:
    """Confirm an opt-out with a fixed one-line text (#72), persisted like any other send."""
    _send_and_persist(
        sender,
        make_session,
        trigger_sid=message_sid,
        to=to,
        body=build_stop_confirmation(business_name),
    )


def send_help_reply(
    sender: SmsSender | None,
    business_name: str | None,
    message_sid: str,
    to: str,
    make_session: SessionFactory,
) -> None:
    """Answer HELP with the fixed reply-to-here instructions (#72), persisted."""
    _send_and_persist(
        sender,
        make_session,
        trigger_sid=message_sid,
        to=to,
        body=build_help_reply(business_name),
    )
