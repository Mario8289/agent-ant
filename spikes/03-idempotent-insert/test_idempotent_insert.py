from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Jsonb
from store import (
    DATABASE_URL,
    INSERT,
    connect,
    count_events,
    create_schema,
    insert_event,
)
from webhook import app

SYNTHETIC = {
    "CallSid": "CA00000000000000000000000000000001",
    "From": "+447000000000",
    "To": "+447000000001",
}


@pytest.fixture
def conn() -> Iterator[psycopg.Connection]:
    try:
        connection = connect()
    except psycopg.OperationalError as exc:
        pytest.skip(f"Postgres not reachable at {DATABASE_URL.split('@')[-1]}: {exc}")
    with connection:
        create_schema(connection)
        connection.execute("TRUNCATE spike03_inbound_events")
        yield connection


def _insert(conn: psycopg.Connection, key: str = SYNTHETIC["CallSid"]) -> bool:
    return insert_event(conn, key, SYNTHETIC["From"], datetime.now(UTC), SYNTHETIC)


def test_constraint_rejects_duplicate_key(conn: psycopg.Connection) -> None:
    # A plain INSERT (no ON CONFLICT) proves the database itself enforces uniqueness,
    # independent of insert_event's handling.
    args = (SYNTHETIC["CallSid"], SYNTHETIC["From"], datetime.now(UTC), Jsonb(SYNTHETIC))
    conn.execute(INSERT, args)
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute(INSERT, args)
    assert count_events(conn, SYNTHETIC["CallSid"]) == 1


def test_duplicate_is_handled_not_a_crash(conn: psycopg.Connection) -> None:
    assert _insert(conn) is True
    assert _insert(conn) is False
    assert count_events(conn, SYNTHETIC["CallSid"]) == 1


def test_connection_stays_usable_after_duplicate(conn: psycopg.Connection) -> None:
    _insert(conn)
    _insert(conn)
    assert _insert(conn, "CA00000000000000000000000000000002") is True


def test_different_keys_are_both_stored(conn: psycopg.Connection) -> None:
    assert _insert(conn, "CA00000000000000000000000000000003") is True
    assert _insert(conn, "CA00000000000000000000000000000004") is True


def test_concurrent_duplicates_store_exactly_one(conn: psycopg.Connection) -> None:
    # Simultaneous retries are the case a check-then-insert gets wrong.
    def attempt(_: int) -> bool:
        with connect() as own:
            return _insert(own)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attempt, range(8)))

    assert results.count(True) == 1
    assert results.count(False) == 7
    assert count_events(conn, SYNTHETIC["CallSid"]) == 1


def test_webhook_retry_returns_200_and_stores_once(conn: psycopg.Connection) -> None:
    client = TestClient(app)
    first = client.post("/webhook/voice", data=SYNTHETIC)
    retry = client.post("/webhook/voice", data=SYNTHETIC)

    assert first.status_code == 200
    assert first.headers["x-duplicate"] == "false"
    assert retry.status_code == 200
    assert retry.headers["x-duplicate"] == "true"
    assert count_events(conn, SYNTHETIC["CallSid"]) == 1
