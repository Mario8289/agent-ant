"""Inbound Twilio webhooks."""

import logging
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_api.security import verified_twilio_form
from agent_ant_api.sms import SmsSender, get_sms_sender, send_missed_call_sms
from agent_ant_core.config import Settings, get_settings
from agent_ant_core.db.idempotency import persist_raw_event
from agent_ant_core.db.models import RawEvent
from agent_ant_core.db.session import get_sessionmaker

logger = logging.getLogger(__name__)

router = APIRouter()

# Fixed text only: the AI never writes free text to customers (D-004). Spoken to the caller
# whose call was forwarded here because the tradesperson did not answer.
MISSED_CALL_TWIML = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<Response>"
    "<Say>Sorry we missed your call. We will send you a text message shortly.</Say>"
    "<Hangup/>"
    "</Response>"
)


def get_session() -> Iterator[Session]:
    with get_sessionmaker()() as session:
        yield session


@router.post("/webhooks/missed-call")
def missed_call(
    form: Annotated[dict[str, str], Depends(verified_twilio_form)],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    sms_sender: Annotated[SmsSender | None, Depends(get_sms_sender)],
    background: BackgroundTasks,
) -> Response:
    """Persist the call, then answer fast.

    Persist before processing (rule 2): the raw event is committed before Twilio is told 200,
    so a crash later cannot lose the job. A retry of the same ``CallSid`` gets the same 200
    but is not stored again, and only a first delivery starts follow-up work (the text), so a
    duplicate can never send a second SMS.
    """
    call_sid = form.get("CallSid")
    caller = form.get("From")
    if not call_sid or not caller:
        raise HTTPException(status_code=400, detail="CallSid and From are required")

    inserted = persist_raw_event(
        session,
        idempotency_key=call_sid,
        source="voice_call",
        caller_number=caller,
        received_at=datetime.now(UTC),
        payload=form,
    )
    session.commit()

    if inserted:
        background.add_task(
            send_missed_call_sms, sms_sender, settings.business_name, call_sid, caller
        )

    # CallSid only: caller numbers are personal data and stay out of logs.
    logger.info("missed call %s: %s", call_sid, "stored" if inserted else "duplicate ignored")
    return Response(content=MISSED_CALL_TWIML, media_type="application/xml")


@router.post("/webhooks/sms-reply")
def sms_reply(
    form: Annotated[dict[str, str], Depends(verified_twilio_form)],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    """Persist the caller's reply, linked to their most recent missed call.

    Keyed on ``MessageSid`` (rule 3). The link is a plain lookup by caller number, so a reply
    from a caller with no missed call is still stored, just unlinked. Linking is by number
    because the reply is sent to the same number that was called. Replies are never acted on
    here: extraction is Week 2.
    """
    message_sid = form.get("MessageSid")
    caller = form.get("From")
    if not message_sid or not caller:
        raise HTTPException(status_code=400, detail="MessageSid and From are required")

    related_id = session.execute(
        select(RawEvent.id)
        .where(RawEvent.source == "voice_call", RawEvent.caller_number == caller)
        .order_by(RawEvent.received_at.desc(), RawEvent.id.desc())
        .limit(1)
    ).scalar_one_or_none()

    inserted = persist_raw_event(
        session,
        idempotency_key=message_sid,
        source="sms_reply",
        caller_number=caller,
        received_at=datetime.now(UTC),
        payload=form,
        related_event_id=related_id,
    )
    session.commit()

    logger.info("sms reply %s: %s", message_sid, "stored" if inserted else "duplicate ignored")
    return Response(status_code=200)
