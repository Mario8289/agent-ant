"""Inbound Twilio webhooks."""

import logging
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from agent_ant_api.security import verified_twilio_form
from agent_ant_core.db.idempotency import persist_raw_event
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
) -> Response:
    """Persist the call, then answer fast.

    Persist before processing (rule 2): the raw event is committed before Twilio is told 200,
    so a crash later cannot lose the job. A retry of the same ``CallSid`` gets the same 200
    but is not stored again, and only a first delivery should ever start follow-up work.
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

    # CallSid only: caller numbers are personal data and stay out of logs.
    logger.info("missed call %s: %s", call_sid, "stored" if inserted else "duplicate ignored")
    return Response(content=MISSED_CALL_TWIML, media_type="application/xml")
