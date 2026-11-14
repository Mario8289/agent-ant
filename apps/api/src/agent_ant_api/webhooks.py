"""Inbound Twilio webhooks."""

import logging
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_api.extraction import SessionFactory, extract_reply, get_llm, get_session_factory
from agent_ant_api.security import verified_twilio_form
from agent_ant_api.sms import (
    SmsSender,
    get_sms_sender,
    is_help_keyword,
    is_stop_keyword,
    send_help_reply,
    send_missed_call_sms,
    send_stop_confirmation,
)
from agent_ant_core.config import Settings, get_settings
from agent_ant_core.db.idempotency import persist_raw_event
from agent_ant_core.db.models import RawEvent
from agent_ant_core.db.opt_out import is_opted_out, record_opt_out
from agent_ant_core.db.outbound_sms import apply_status_callback
from agent_ant_core.db.session import get_sessionmaker
from agent_ant_core.llm import LLM

logger = logging.getLogger(__name__)

router = APIRouter()


# Fixed text only: the AI never writes free text to customers (D-004). Spoken to the caller
# whose call was forwarded here because the tradesperson did not answer.
def build_missed_call_twiml(public_base_url: str | None) -> str:
    """TwiML that prompts for a voicemail and asks Twilio to transcribe it (#33).

    The caller hears a fixed prompt and can leave a message. Twilio records it and, after the
    call ends, transcribes it and POSTs the transcript to the transcription webhook. The
    ``transcribeCallback`` needs the public URL Twilio can reach; without a configured public
    base it falls back to a relative path, which Twilio resolves against the voice webhook's host.
    """
    callback = (
        f"{public_base_url.rstrip('/')}/webhooks/voicemail-transcription"
        if public_base_url
        else "/webhooks/voicemail-transcription"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response>"
        "<Say>Sorry we missed your call. Please leave a message after the tone and we'll get "
        "back to you.</Say>"
        f'<Record transcribe="true" transcribeCallback="{callback}" maxLength="60" />'
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
    session_factory: Annotated[SessionFactory, Depends(get_session_factory)],
    background: BackgroundTasks,
) -> Response:
    """Persist the call, then answer fast.

    Persist before processing (rule 2): the raw event is committed before Twilio is told 200,
    so a crash later cannot lose the job. A retry of the same ``CallSid`` gets the same 200
    but is not stored again, and only a first delivery starts follow-up work (the text), so a
    duplicate can never send a second SMS. A caller who has opted out (D-019) is never texted,
    but the call is still stored so the tradesperson can ring them back.
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

    if inserted and not is_opted_out(session, caller):
        background.add_task(
            send_missed_call_sms,
            sms_sender,
            settings.business_name,
            call_sid,
            caller,
            session_factory,
        )

    # CallSid only: caller numbers are personal data and stay out of logs.
    logger.info("missed call %s: %s", call_sid, "stored" if inserted else "duplicate ignored")
    return Response(
        content=build_missed_call_twiml(settings.public_base_url),
        media_type="application/xml",
    )


@router.post("/webhooks/sms-reply")
def sms_reply(
    form: Annotated[dict[str, str], Depends(verified_twilio_form)],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    llm: Annotated[LLM | None, Depends(get_llm)],
    session_factory: Annotated[SessionFactory, Depends(get_session_factory)],
    sms_sender: Annotated[SmsSender | None, Depends(get_sms_sender)],
    background: BackgroundTasks,
) -> Response:
    """Persist the caller's reply, linked to their most recent missed call.

    Keyed on ``MessageSid`` (rule 3). The link is a plain lookup by caller number, so a reply
    from a caller with no missed call is still stored, just unlinked. Linking is by number
    because the reply is sent to the same number that was called. After storing, extraction runs
    in the background; a duplicate delivery stores nothing and starts no second extraction.

    STOP and HELP are handled here and never reach extraction (#72, D-019): STOP records an
    opt-out and confirms it, HELP answers with the fixed reply-to-here instructions. Both are
    fixed templates (D-004), and a duplicate delivery sends nothing a second time.
    """
    message_sid = form.get("MessageSid")
    caller = form.get("From")
    if not message_sid or not caller:
        raise HTTPException(status_code=400, detail="MessageSid and From are required")

    body = form.get("Body", "")

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

    if inserted:
        if is_stop_keyword(body):
            record_opt_out(session, caller)
            session.commit()
            background.add_task(
                send_stop_confirmation,
                sms_sender,
                settings.business_name,
                message_sid,
                caller,
                session_factory,
            )
        elif is_help_keyword(body):
            background.add_task(
                send_help_reply,
                sms_sender,
                settings.business_name,
                message_sid,
                caller,
                session_factory,
            )
        else:
            background.add_task(
                extract_reply,
                llm,
                settings.llm_model or "unconfigured",
                message_sid,
                session_factory,
            )

    logger.info("sms reply %s: %s", message_sid, "stored" if inserted else "duplicate ignored")
    return Response(status_code=200)


@router.post("/webhooks/voicemail-transcription")
def voicemail_transcription(
    form: Annotated[dict[str, str], Depends(verified_twilio_form)],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    llm: Annotated[LLM | None, Depends(get_llm)],
    session_factory: Annotated[SessionFactory, Depends(get_session_factory)],
    background: BackgroundTasks,
) -> Response:
    """Persist a voicemail transcript and run extraction over it (#33).

    Twilio posts here asynchronously when it finishes transcribing a voicemail (``<Record
    transcribe="true">``). Keyed on ``RecordingSid`` (rule 3) and linked to the missed call by
    ``CallSid`` — a stronger link than the SMS reply's number heuristic, because the callback
    carries the call's own identifier. A completed transcript runs the same extraction pipeline
    as a reply; a failed transcription is stored but not extracted (there is no text to work
    with), and a duplicate delivery stores nothing and starts no second extraction.
    """
    recording_sid = form.get("RecordingSid")
    caller = form.get("From")
    if not recording_sid or not caller:
        raise HTTPException(status_code=400, detail="RecordingSid and From are required")

    call_sid = form.get("CallSid")
    related_id = None
    if call_sid:
        related_id = session.execute(
            select(RawEvent.id)
            .where(RawEvent.source == "voice_call", RawEvent.idempotency_key == call_sid)
            .limit(1)
        ).scalar_one_or_none()

    inserted = persist_raw_event(
        session,
        idempotency_key=recording_sid,
        source="voicemail",
        caller_number=caller,
        received_at=datetime.now(UTC),
        payload=form,
        related_event_id=related_id,
    )
    session.commit()

    if inserted and form.get("TranscriptionStatus") == "completed":
        background.add_task(
            extract_reply,
            llm,
            settings.llm_model or "unconfigured",
            recording_sid,
            session_factory,
        )

    logger.info("voicemail %s: %s", recording_sid, "stored" if inserted else "duplicate ignored")
    return Response(status_code=200)


@router.post("/webhooks/sms-status")
def sms_status(
    form: Annotated[dict[str, str], Depends(verified_twilio_form)],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    """Twilio's delivery-status callback: update the outbound row by MessageSid (#73).

    Twilio posts here when a message moves to ``delivered``, ``undelivered``, ``failed``, etc.
    The update is idempotent — a duplicate callback sets the same status again and creates
    nothing — and an unknown SID (a message sent before this table existed) is ignored.
    """
    twilio_sid = form.get("MessageSid")
    status = form.get("MessageStatus")
    if not twilio_sid or not status:
        raise HTTPException(status_code=400, detail="MessageSid and MessageStatus are required")

    apply_status_callback(session, twilio_sid, status, form.get("ErrorCode") or None)
    session.commit()
    return Response(status_code=200)
