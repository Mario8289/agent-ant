"""Tests for raw-event persistence and the baseline migration.

The ``engine`` and ``session`` fixtures live in the root ``conftest.py`` (needs
``TEST_DATABASE_URL``; see migrations/README.md).
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import pytest
from sqlalchemy import Engine, func, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from agent_ant_core.db.idempotency import persist_raw_event
from agent_ant_core.db.models import RawEvent

CALL_SID = "CA00000000000000000000000000000001"
PAYLOAD = {"CallSid": CALL_SID, "From": "+447000000000", "To": "+447000000001"}


def _persist(db: Session, key: str = CALL_SID) -> bool:
    inserted = persist_raw_event(
        db,
        idempotency_key=key,
        source="voice_call",
        caller_number=PAYLOAD["From"],
        received_at=datetime.now(UTC),
        payload=PAYLOAD,
    )
    db.commit()
    return inserted


def _count(db: Session, key: str = CALL_SID) -> int:
    stmt = select(func.count()).select_from(RawEvent).where(RawEvent.idempotency_key == key)
    return db.execute(stmt).scalar_one()


def test_migration_creates_the_unique_constraint(engine: Engine) -> None:
    constraints = inspect(engine).get_unique_constraints("raw_events")
    assert [c["column_names"] for c in constraints] == [["idempotency_key"]]


def test_new_event_is_stored_exactly_as_received(session: Session) -> None:
    assert _persist(session) is True

    row = session.execute(select(RawEvent)).scalar_one()
    assert row.idempotency_key == CALL_SID
    assert row.source == "voice_call"
    assert row.caller_number == "+447000000000"
    assert row.payload == PAYLOAD
    assert row.received_at.tzinfo is not None


def test_duplicate_delivery_is_a_no_op(session: Session) -> None:
    assert _persist(session) is True
    assert _persist(session) is False
    assert _count(session) == 1


def test_session_stays_usable_after_a_duplicate(session: Session) -> None:
    _persist(session)
    _persist(session)
    assert _persist(session, "CA00000000000000000000000000000002") is True


def test_different_keys_are_both_stored(session: Session) -> None:
    assert _persist(session, "CA00000000000000000000000000000003") is True
    assert _persist(session, "CA00000000000000000000000000000004") is True


def test_concurrent_duplicates_store_exactly_one(engine: Engine, session: Session) -> None:
    # Simultaneous retries are the case a check-then-insert gets wrong.
    def attempt(_: int) -> bool:
        with Session(engine) as own:
            return _persist(own)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attempt, range(8)))

    assert results.count(True) == 1
    assert results.count(False) == 7
    assert _count(session) == 1


def test_the_database_itself_rejects_a_duplicate_key(session: Session) -> None:
    # A plain ORM insert (no ON CONFLICT) proves the constraint, not our helper, does the work.
    def row() -> RawEvent:
        return RawEvent(
            idempotency_key=CALL_SID,
            source="voice_call",
            caller_number="+447000000000",
            received_at=datetime.now(UTC),
            payload=PAYLOAD,
        )

    session.add(row())
    session.commit()
    session.add(row())
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_unknown_source_is_rejected(session: Session) -> None:
    session.add(
        RawEvent(
            idempotency_key=CALL_SID,
            source="carrier_pigeon",
            caller_number="+447000000000",
            received_at=datetime.now(UTC),
            payload=PAYLOAD,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
