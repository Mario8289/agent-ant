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
from twilio.http.http_client import TwilioHttpClient
from twilio.rest import Client

from agent_ant_core.config import Settings, get_settings

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

# Sends one text: (to, body). None when Twilio is not configured.
SmsSender = Callable[[str, str], None]


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
    """A Twilio-backed sender, or None if account, token or from-number is missing."""
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

    def send(to: str, body: str) -> None:
        message = client.messages.create(to=to, from_=from_number, body=body)
        logger.info("sms %s accepted by twilio", message.sid)

    return send


def _send(sender: SmsSender | None, to: str, body: str, sid: str) -> None:
    """Send one text and never raise. Logs with ``sid`` (CallSid or MessageSid) so it can be found.

    The webhook has already answered Twilio by the time this runs, so a send failure is logged,
    not re-thrown. There is no retry or outbox yet (#34), so a failed or lost send is not
    recovered automatically.
    """
    if sender is None:
        logger.warning("%s: twilio is not configured, no sms sent", sid)
        return
    try:
        sender(to, body)
    except Exception:
        # Broad on purpose: Twilio API errors and network timeouts are different exception
        # types, and none of them may escape a background task.
        logger.exception("%s: sms send failed", sid)


def send_missed_call_sms(
    sender: SmsSender | None, business_name: str | None, call_sid: str, to: str
) -> None:
    """Send the missed-call template text."""
    _send(sender, to, build_missed_call_message(business_name), call_sid)


def send_stop_confirmation(
    sender: SmsSender | None, business_name: str | None, message_sid: str, to: str
) -> None:
    """Confirm an opt-out with a fixed one-line text (#72)."""
    _send(sender, to, build_stop_confirmation(business_name), message_sid)


def send_help_reply(
    sender: SmsSender | None, business_name: str | None, message_sid: str, to: str
) -> None:
    """Answer HELP with the fixed reply-to-here instructions (#72)."""
    _send(sender, to, build_help_reply(business_name), message_sid)
