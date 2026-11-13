"""Background extraction of a stored reply (Week 2 integration, #34 retry).

Runs after the webhook has already stored the reply and answered Twilio, so a slow or failing
model call can never delay or fail the webhook. The provider seam (``get_llm``) returns None
when ``LLM_PROVIDER`` / ``LLM_MODEL`` are unset (D-009), so extraction is skipped rather than
attempted against a missing client.

The background task opens its own session through an injected factory: the webhook's request
session is already closed by the time the task runs, and injecting the factory keeps the task
testable against a throwaway database.

#34 adds retry: every attempt bumps ``raw_events.extraction_attempts`` and records an
``extraction_status`` (``done`` / ``failed`` / ``dead``). A reply whose extraction failed or
never ran is recovered by ``retry_failed_extractions``, run on a schedule via
``just retry-extractions``.
"""

import logging
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_api.notify import notify_support
from agent_ant_core.config import Settings, get_settings
from agent_ant_core.db.extraction import (
    DEAD,
    DONE,
    FAILED,
    MAX_EXTRACTION_ATTEMPTS,
    candidate_replies,
)
from agent_ant_core.db.models import RawEvent
from agent_ant_core.db.session import get_sessionmaker
from agent_ant_core.llm import LLM, build_llm
from agent_ant_missed_call.processor import process_reply

logger = logging.getLogger(__name__)

# A callable that hands out a fresh session, e.g. ``sessionmaker()`` or a test-bound factory.
SessionFactory = Callable[[], Session]


def get_llm(settings: Annotated[Settings, Depends(get_settings)]) -> LLM | None:
    """Return the provider for extraction, or None when none is configured (D-009)."""
    return build_llm(settings)


def get_session_factory() -> SessionFactory:
    """Return a factory that opens a session on the configured database."""
    maker = get_sessionmaker()
    return lambda: maker()


def _extract_one(session: Session, llm: LLM, model: str, reply: RawEvent) -> int | None:
    """Run one extraction attempt over a reply, recording the attempt and its outcome.

    Returns the new job id on success, ``None`` on failure (invalid output or a raised model
    call). Never raises: an exception is rolled back and the reply is marked ``failed`` in a fresh
    transaction, so a provider outage surfaces as a retryable row rather than a silent drop. Each
    call commits or rolls back; the caller does not own the transaction.
    """
    raw_event_id = reply.id
    message_sid = reply.idempotency_key
    body = (reply.payload or {}).get("Body", "")

    try:
        job_id = process_reply(
            session,
            llm,
            raw_event_id=raw_event_id,
            idempotency_key=message_sid,
            caller_number=reply.caller_number,
            received_at=reply.received_at,
            message=body,
            model=model,
        )
    except Exception:
        # Broad on purpose: a model, parse or DB failure must not escape the background task. The
        # rollback discards the partial extraction; a fresh fetch records the failed attempt.
        session.rollback()
        failed_reply = session.get(RawEvent, raw_event_id)
        assert failed_reply is not None  # the reply was committed before the attempt
        failed_reply.extraction_attempts = (failed_reply.extraction_attempts or 0) + 1
        failed_reply.extraction_status = FAILED
        session.commit()
        logger.exception("sms reply %s: extraction failed", message_sid)
        return None

    reply.extraction_attempts = (reply.extraction_attempts or 0) + 1
    reply.extraction_status = DONE if job_id is not None else FAILED
    session.commit()
    return job_id


def extract_reply(
    llm: LLM | None, model: str, message_sid: str, make_session: SessionFactory
) -> None:
    """Extract the stored reply and persist the job + audit row. Never raises.

    Looks the reply up by ``MessageSid``; the webhook already committed the raw event before
    this runs, so it is always present.
    """
    if llm is None:
        logger.warning("sms reply %s: no llm configured, extraction skipped", message_sid)
        return

    with make_session() as session:
        reply = session.execute(
            select(RawEvent).where(RawEvent.idempotency_key == message_sid)
        ).scalar_one_or_none()
        if reply is None:
            logger.warning("sms reply %s: raw event missing, extraction skipped", message_sid)
            return

        job_id = _extract_one(session, llm, model, reply)

    outcome = f"job {job_id} captured" if job_id else "extraction flagged for review"
    logger.info("sms reply %s: %s", message_sid, outcome)


def retry_failed_extractions(
    session: Session,
    llm: LLM,
    model: str,
    *,
    max_attempts: int = MAX_EXTRACTION_ATTEMPTS,
) -> int:
    """Re-run extraction over every retryable reply; dead-letter those that exhaust retries.

    Run on a schedule by ``scripts/retry_extractions.py``. A reply still ``failed`` once it has
    reached ``max_attempts`` is promoted to ``dead`` so the dashboard's failure panel can't miss
    it. Returns the number of jobs recovered. The caller owns the outer session and commits any
    final dead-letter bookkeeping; ``_extract_one`` commits per reply.
    """
    recovered = 0
    for candidate in candidate_replies(session, max_attempts=max_attempts):
        raw_event_id = candidate.id
        job_id = _extract_one(session, llm, model, candidate)
        if job_id is not None:
            recovered += 1
            continue

        reply = session.get(RawEvent, raw_event_id)
        assert reply is not None
        if reply.extraction_status == FAILED and (reply.extraction_attempts or 0) >= max_attempts:
            message_sid = reply.idempotency_key
            reply.extraction_status = DEAD
            session.commit()
            notify_support(
                f"extraction dead-lettered for reply {message_sid} — needs manual filing"
            )

    return recovered
