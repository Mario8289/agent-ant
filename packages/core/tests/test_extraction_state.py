"""Extraction retry state: candidate selection and the failure panel query (issue #34)."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from agent_ant_core.db.extraction import (
    DEAD,
    DONE,
    FAILED,
    candidate_replies,
    list_failed_extractions,
)
from agent_ant_core.db.models import RawEvent

NUMBER = "+447000000000"


def _reply(session: Session, key: str, *, status: str | None = None, attempts: int = 0) -> RawEvent:
    row = RawEvent(
        idempotency_key=key,
        source="sms_reply",
        caller_number=NUMBER,
        received_at=datetime.now(UTC),
        payload={"Body": "fix a tap"},
        extraction_status=status,
        extraction_attempts=attempts,
    )
    session.add(row)
    session.commit()
    return row


def test_candidates_are_never_run_or_failed_replies(session: Session) -> None:
    never = _reply(session, "SM1")
    failed = _reply(session, "SM2", status=FAILED, attempts=1)
    _reply(session, "SM3", status=DONE, attempts=1)
    _reply(session, "SM4", status=FAILED, attempts=3)  # at the bound

    candidates = candidate_replies(session)

    assert {r.idempotency_key for r in candidates} == {
        never.idempotency_key,
        failed.idempotency_key,
    }


def test_candidates_skip_voice_calls(session: Session) -> None:
    session.add(
        RawEvent(
            idempotency_key="CA1",
            source="voice_call",
            caller_number=NUMBER,
            received_at=datetime.now(UTC),
            payload={},
        )
    )
    session.commit()

    assert candidate_replies(session) == []


def test_candidates_include_voicemail_transcripts(session: Session) -> None:
    session.add(
        RawEvent(
            idempotency_key="RE1",
            source="voicemail",
            caller_number=NUMBER,
            received_at=datetime.now(UTC),
            payload={"TranscriptionText": "fix a tap"},
        )
    )
    session.commit()

    candidates = candidate_replies(session)

    assert [r.idempotency_key for r in candidates] == ["RE1"]


def test_failure_panel_lists_failed_and_dead_replies(session: Session) -> None:
    failed = _reply(session, "SM1", status=FAILED, attempts=1)
    dead = _reply(session, "SM2", status=DEAD, attempts=3)
    _reply(session, "SM3", status=DONE, attempts=1)
    _reply(session, "SM4")  # never run

    messages = list_failed_extractions(session)

    assert {r.idempotency_key for r in messages} == {failed.idempotency_key, dead.idempotency_key}
