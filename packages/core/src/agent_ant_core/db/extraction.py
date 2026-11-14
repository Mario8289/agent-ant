"""Extraction retry state and queries (issue #34).

A reply's extraction can fail two ways: the model returned something that still failed Pydantic
validation after its bounded repairs (``validated=False``, no job), or the model call raised
(provider down, throttled). Both used to be swallowed by the background task and left no way to
retry them except by hand. The state here — ``extraction_attempts`` and ``extraction_status`` on
``raw_events`` — turns that into a retryable, dead-letterable queue, exactly like the SMS send
path (D-023).

Statuses: ``NULL`` = never attempted, ``done`` = a job was captured, ``failed`` = the last
attempt did not produce a job, ``dead`` = retries exhausted, needs a human.

A "reply" here is any extracted inbound event — an SMS reply or a voicemail transcript (issue
#33). Both run the same extraction pipeline, so both are retryable and dead-letterable.
"""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from agent_ant_core.db.models import RawEvent

# A failed extraction is retried up to this many attempts (including the first), then dead-lettered.
MAX_EXTRACTION_ATTEMPTS = 3

DONE = "done"
FAILED = "failed"
DEAD = "dead"

# Sources that carry text we extract a job from. Voice calls are recorded but never extracted.
EXTRACTED_SOURCES = ("sms_reply", "voicemail")


def candidate_replies(
    session: Session, *, max_attempts: int = MAX_EXTRACTION_ATTEMPTS
) -> list[RawEvent]:
    """Events that still need an extraction attempt: never done, under the attempt bound.

    Includes replies whose extraction never ran (a crash between the webhook commit and the
    background task, or an event stored while ``llm`` was unset) as well as ``failed`` ones. The
    idempotent ``persist_job_record`` keeps a concurrent retry from creating a second job.
    """
    return list(
        session.execute(
            select(RawEvent)
            .where(
                RawEvent.source.in_(EXTRACTED_SOURCES),
                or_(
                    RawEvent.extraction_status.is_(None),
                    RawEvent.extraction_status == FAILED,
                ),
                RawEvent.extraction_attempts < max_attempts,
            )
            .order_by(RawEvent.received_at.asc(), RawEvent.id.asc())
        ).scalars()
    )


def list_failed_extractions(session: Session, *, limit: int = 20) -> list[RawEvent]:
    """Events whose extraction failed or is dead-lettered, newest first, for the dashboard."""
    return list(
        session.execute(
            select(RawEvent)
            .where(
                RawEvent.source.in_(EXTRACTED_SOURCES),
                RawEvent.extraction_status.in_((FAILED, DEAD)),
            )
            .order_by(RawEvent.received_at.desc(), RawEvent.id.desc())
            .limit(limit)
        ).scalars()
    )
