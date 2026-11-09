"""Shared fixtures for tests that need a real Postgres.

The guarantees under test (unique constraints, idempotent inserts) are database behaviour, so
SQLite cannot stand in. Point ``TEST_DATABASE_URL`` at a throwaway database: the fixtures run
the Alembic migrations against it and ``TRUNCATE raw_events`` before each test. Without the
variable the tests skip locally and fail under CI, so a missing database cannot hide in a
green build.
"""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

REPO_ROOT = Path(__file__).resolve().parent


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        message = "TEST_DATABASE_URL is not set (see migrations/README.md)"
        if os.environ.get("CI"):
            pytest.fail(message)
        pytest.skip(message)

    config = Config(str(REPO_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    command.downgrade(config, "base")
    command.upgrade(config, "head")

    test_engine = create_engine(url)
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE raw_events, job_records, llm_output_audits, human_edits"))
    with Session(engine) as db:
        yield db
