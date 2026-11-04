from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from agent_ant_missed_call.schemas import JobRecord


def _record(**overrides: object) -> JobRecord:
    now = datetime.now(UTC)
    data: dict[str, object] = {
        "idempotency_key": "SM123",
        "caller_number": "+447700900123",
        "received_at": now,
        "raw_message": "Hi, need a shelf fitting Saturday",
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return JobRecord.model_validate(data)


def test_minimal_record_defaults_to_captured_and_unknown_urgency() -> None:
    record = _record()
    assert record.status == "captured"
    assert record.urgency == "unknown"
    assert record.job_type is None


def test_idempotency_key_is_required() -> None:
    with pytest.raises(ValidationError):
        _record(idempotency_key="")


def test_unknown_status_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _record(status="confirmed")


def test_confidence_is_bounded() -> None:
    with pytest.raises(ValidationError):
        _record(extraction_confidence=1.5)
