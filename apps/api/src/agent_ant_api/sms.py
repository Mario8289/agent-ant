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

# Sends one text: (to, body). None when Twilio is not configured.
SmsSender = Callable[[str, str], None]


def build_missed_call_message(business_name: str | None) -> str:
    if business_name:
        return TEMPLATE_WITH_NAME.format(business_name=business_name)
    return TEMPLATE_WITHOUT_NAME


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


def send_missed_call_sms(
    sender: SmsSender | None, business_name: str | None, call_sid: str, to: str
) -> None:
    """Send the template text. Never raises: the webhook has already answered Twilio.

    A failure is logged with the CallSid so it can be found, but the caller number stays out of
    the logs. There is no retry or outbox yet, so a failed or lost send is not recovered
    automatically; that is Week 5 (#34).
    """
    if sender is None:
        logger.warning("call %s: twilio is not configured, no sms sent", call_sid)
        return
    try:
        sender(to, build_missed_call_message(business_name))
    except Exception:
        # Broad on purpose: Twilio API errors and network timeouts are different exception
        # types, and none of them may escape a background task.
        logger.exception("call %s: sms send failed", call_sid)
