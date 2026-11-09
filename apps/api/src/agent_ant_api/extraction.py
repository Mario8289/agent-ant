"""Background extraction of a stored reply (Week 2 integration).

Runs after the webhook has already stored the reply and answered Twilio, so a slow or failing
model call can never delay or fail the webhook. The provider seam (``get_llm``) returns None
until a Bedrock-backed adapter lands (D-009, ``docs/10``), so extraction is skipped rather than
attempted against a missing client.

The background task opens its own session through an injected factory: the webhook's request
session is already closed by the time the task runs, and injecting the factory keeps the task
testable against a throwaway database.
"""

import logging
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_core.config import Settings, get_settings
from agent_ant_core.db.models import RawEvent
from agent_ant_core.db.session import get_sessionmaker
from agent_ant_core.llm import LLM
from agent_ant_missed_call.processor import process_reply

logger = logging.getLogger(__name__)

# A callable that hands out a fresh session, e.g. ``sessionmaker()`` or a test-bound factory.
SessionFactory = Callable[[], Session]


def get_llm(settings: Annotated[Settings, Depends(get_settings)]) -> LLM | None:
    """Return the provider for extraction, or None when none is configured.

    The Bedrock adapter that satisfies ``LLM`` is written once the credentials checklist in
    ``docs/10`` is done (D-009). Until then there is no provider to hand out, and extraction
    is skipped.
    """
    return None  # TODO(#22 real call): return a Bedrock-backed LLM when llm_provider is set.


def get_session_factory() -> SessionFactory:
    """Return a factory that opens a session on the configured database."""
    maker = get_sessionmaker()
    return lambda: maker()


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

        body = (reply.payload or {}).get("Body", "")
        try:
            job_id = process_reply(
                session,
                llm,
                raw_event_id=reply.id,
                idempotency_key=message_sid,
                caller_number=reply.caller_number,
                received_at=reply.received_at,
                message=body,
                model=model,
            )
        except Exception:
            # Broad on purpose: a model, parse or DB failure must not escape the background task.
            session.rollback()
            logger.exception("sms reply %s: extraction failed", message_sid)
            return

        session.commit()
        outcome = f"job {job_id} captured" if job_id else "extraction flagged for review"
        logger.info("sms reply %s: %s", message_sid, outcome)
