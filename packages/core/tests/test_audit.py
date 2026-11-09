"""Tests for the audit trail: LLM output and human edit recording (issue #24).

Needs ``TEST_DATABASE_URL`` like ``test_raw_events.py`` — the guarantees under test (foreign
keys, the non-negative check) are database behaviour, so SQLite cannot stand in.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy import Engine, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from agent_ant_core.audit.records import record_human_edit, record_llm_output
from agent_ant_core.db.idempotency import persist_raw_event
from agent_ant_core.db.models import HumanEdit, LLMOutputAudit, RawEvent

MESSAGE_SID = "SM00000000000000000000000000000001"


def _store_reply(session: Session) -> int:
    """Persist a synthetic SMS reply and return its raw_events id."""
    persist_raw_event(
        session,
        idempotency_key=MESSAGE_SID,
        source="sms_reply",
        caller_number="+447000000000",
        received_at=datetime.now(UTC),
        payload={"MessageSid": MESSAGE_SID, "Body": "need a wardrobe fitted"},
    )
    session.flush()
    return session.execute(select(RawEvent.id)).scalar_one()


def test_audit_tables_are_created_with_foreign_keys(engine: Engine) -> None:
    tables = inspect(engine).get_table_names()
    assert "llm_output_audits" in tables
    assert "human_edits" in tables

    edit_fks = inspect(engine).get_foreign_keys("human_edits")
    assert [fk["constrained_columns"] for fk in edit_fks] == [["llm_output_id"]]


def test_record_llm_output_persists_the_extraction(session: Session) -> None:
    event_id = _store_reply(session)
    audit_id = record_llm_output(
        session,
        raw_event_id=event_id,
        model="anthropic.claude-3-haiku-20240307-v1:0",
        prompt_version="v1",
        raw_output='{"name": null, "job_type": "wardrobe fitting"}',
        validated=True,
    )
    session.commit()

    row = session.execute(select(LLMOutputAudit)).scalar_one()
    assert row.id == audit_id
    assert row.raw_event_id == event_id
    assert row.model == "anthropic.claude-3-haiku-20240307-v1:0"
    assert row.prompt_version == "v1"
    assert row.raw_output == '{"name": null, "job_type": "wardrobe fitting"}'
    assert row.validated is True
    assert row.repair_attempts == 0
    assert row.job_id is None
    assert row.created_at is not None


def test_record_llm_output_records_invalid_extractions_too(session: Session) -> None:
    event_id = _store_reply(session)
    record_llm_output(
        session,
        raw_event_id=event_id,
        model="m",
        prompt_version="v1",
        raw_output="not json",
        validated=False,
        repair_attempts=2,
    )
    session.commit()

    row = session.execute(select(LLMOutputAudit)).scalar_one()
    assert row.validated is False
    assert row.repair_attempts == 2


def test_record_human_edit_links_to_the_audit_row(session: Session) -> None:
    event_id = _store_reply(session)
    audit_id = record_llm_output(
        session,
        raw_event_id=event_id,
        model="m",
        prompt_version="v1",
        raw_output="{}",
        validated=True,
    )
    edit_id = record_human_edit(
        session,
        llm_output_id=audit_id,
        edit_diff={"job_type": {"before": None, "after": "wardrobe fitting"}},
    )
    session.commit()

    edit = session.execute(select(HumanEdit)).scalar_one()
    assert edit.id == edit_id
    assert edit.llm_output_id == audit_id
    assert edit.edit_diff["job_type"]["after"] == "wardrobe fitting"


def test_llm_output_requires_an_existing_raw_event(session: Session) -> None:
    session.add(
        LLMOutputAudit(
            raw_event_id=999999,
            model="m",
            prompt_version="v1",
            raw_output="{}",
            validated=True,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_repair_attempts_cannot_be_negative(session: Session) -> None:
    event_id = _store_reply(session)
    session.add(
        LLMOutputAudit(
            raw_event_id=event_id,
            model="m",
            prompt_version="v1",
            raw_output="{}",
            validated=True,
            repair_attempts=-1,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
