"""Extraction retry loop (#34): recovering failed replies and dead-lettering the exhausted."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_api.extraction import retry_failed_extractions
from agent_ant_core.db.extraction import DEAD, DONE, FAILED
from agent_ant_core.db.models import JobRecord, RawEvent
from agent_ant_core.testing import FakeLLM

NUMBER = "+447000000000"
GOOD = '{"name": "Sam", "job_type": "tap", "urgency": "medium"}'


class _RaisingLLM:
    def complete(self, prompt: str) -> str:
        raise RuntimeError("provider down")


def _reply(session: Session, key: str) -> RawEvent:
    row = RawEvent(
        idempotency_key=key,
        source="sms_reply",
        caller_number=NUMBER,
        received_at=datetime.now(UTC),
        payload={"Body": "fix a tap"},
    )
    session.add(row)
    session.commit()
    return row


def test_retry_recovers_a_failed_reply(session: Session) -> None:
    reply = _reply(session, "SM1")
    reply.extraction_status = FAILED
    reply.extraction_attempts = 1
    session.commit()

    recovered = retry_failed_extractions(session, FakeLLM(GOOD), "m")

    assert recovered == 1
    session.expire_all()
    reply = session.get(RawEvent, reply.id)
    assert reply is not None
    assert reply.extraction_status == DONE
    assert reply.extraction_attempts == 2
    assert session.execute(select(JobRecord)).scalar_one().idempotency_key == "SM1"


def test_retry_dead_letters_at_the_bound(session: Session) -> None:
    reply = _reply(session, "SM1")
    reply.extraction_status = FAILED
    reply.extraction_attempts = 2  # one attempt left under the default bound of 3
    session.commit()

    recovered = retry_failed_extractions(session, _RaisingLLM(), "m")

    assert recovered == 0
    session.expire_all()
    reply = session.get(RawEvent, reply.id)
    assert reply is not None
    assert reply.extraction_status == DEAD
    assert reply.extraction_attempts == 3
    assert session.execute(select(JobRecord)).scalars().all() == []


def test_retry_skips_done_replies(session: Session) -> None:
    reply = _reply(session, "SM1")
    reply.extraction_status = DONE
    reply.extraction_attempts = 1
    session.commit()

    assert retry_failed_extractions(session, FakeLLM(GOOD), "m") == 0
