"""#59 Spike 3: idempotent insert backed by a Postgres unique constraint.

Twilio delivers webhooks at least once, so the same CallSid/MessageSid will arrive twice
sooner or later. The dedupe has to live in the database: a check-then-insert in Python
races when two retries land together, whereas a unique constraint is enforced atomically.

`insert_event` uses INSERT ... ON CONFLICT DO NOTHING so a duplicate is an expected outcome
(returns False) rather than an exception that aborts the transaction.
"""

import os
from datetime import datetime
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

# .env.example uses the SQLAlchemy-style "postgresql+psycopg://" scheme; psycopg wants plain.
# Synthetic default matches this spike's docker-compose.yml (port 5433, not the repo's 5432),
# so a bare `pytest` never touches a Postgres you did not start for this spike.
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://agent_ant:agent_ant@localhost:5433/agent_ant"
).replace("postgresql+psycopg://", "postgresql://", 1)

SCHEMA = """
CREATE TABLE IF NOT EXISTS spike03_inbound_events (
    id              bigserial PRIMARY KEY,
    idempotency_key text        NOT NULL UNIQUE,
    caller_number   text        NOT NULL,
    received_at     timestamptz NOT NULL,
    raw_payload     jsonb       NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now()
)
"""

INSERT = """
INSERT INTO spike03_inbound_events (idempotency_key, caller_number, received_at, raw_payload)
VALUES (%s, %s, %s, %s)
"""


def connect() -> psycopg.Connection[Any]:
    return psycopg.connect(DATABASE_URL, autocommit=True)


def create_schema(conn: psycopg.Connection[Any]) -> None:
    conn.execute(SCHEMA)


def insert_event(
    conn: psycopg.Connection[Any],
    idempotency_key: str,
    caller_number: str,
    received_at: datetime,
    raw_payload: dict[str, str],
) -> bool:
    """Store the raw event. Returns True if inserted, False if it was a duplicate."""
    cur = conn.execute(
        INSERT + " ON CONFLICT (idempotency_key) DO NOTHING RETURNING id",
        (idempotency_key, caller_number, received_at, Jsonb(raw_payload)),
    )
    return cur.fetchone() is not None


def count_events(conn: psycopg.Connection[Any], idempotency_key: str) -> int:
    row = conn.execute(
        "SELECT count(*) FROM spike03_inbound_events WHERE idempotency_key = %s",
        (idempotency_key,),
    ).fetchone()
    assert row is not None
    return int(row[0])
