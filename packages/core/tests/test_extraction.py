"""Tests for structured extraction with bounded repair (issue #22)."""

import json

import pytest

from agent_ant_core.llm import ExtractionResult, JobExtraction, extract_job
from agent_ant_core.testing import FakeLLM

MESSAGE = "hi its Sam, boiler has packed in, in Leeds LS6, really urgent, could do tomorrow"
EXTRACT_PROMPT = "Extract: $message"
REPAIR_PROMPT = "Fix: message=$message previous=$previous_output errors=$errors"

VALID = {
    "name": "Sam",
    "job_type": "boiler repair",
    "location": "Leeds LS6",
    "urgency": "high",
    "preferred_date": "tomorrow",
}

EXPECTED = JobExtraction(
    name="Sam",
    job_type="boiler repair",
    location="Leeds LS6",
    urgency="high",
    preferred_date="tomorrow",
)


def _extract(llm: FakeLLM, message: str = MESSAGE, max_repairs: int = 2) -> ExtractionResult:
    return extract_job(
        llm,
        message,
        extract_prompt=EXTRACT_PROMPT,
        repair_prompt=REPAIR_PROMPT,
        prompt_version="extract_v1",
        max_repairs=max_repairs,
    )


def test_messy_text_becomes_a_validated_object() -> None:
    llm = FakeLLM(json.dumps(VALID))
    result = _extract(llm)

    assert result.validated is True
    assert result.repair_attempts == 0
    assert result.job == EXPECTED
    assert len(llm.prompts) == 1
    assert MESSAGE in llm.prompts[0]


def test_missing_fields_default_instead_of_failing() -> None:
    result = _extract(FakeLLM('{"job_type": "leaking tap"}'), message="got a leaky tap")

    assert result.validated is True
    assert result.job is not None
    assert result.job.urgency == "unknown"
    assert result.job.name is None


def test_code_fenced_json_is_accepted() -> None:
    result = _extract(FakeLLM("```json\n" + json.dumps(VALID) + "\n```"))

    assert result.validated is True
    assert result.repair_attempts == 0


def test_invalid_output_is_repaired() -> None:
    bad = json.dumps({**VALID, "urgency": "ASAP!!"})
    llm = FakeLLM(bad, json.dumps(VALID))
    result = _extract(llm)

    assert result.validated is True
    assert result.repair_attempts == 1
    assert result.job == EXPECTED
    assert result.raw_outputs == [bad, json.dumps(VALID)]


def test_repair_prompt_carries_the_error_and_previous_output() -> None:
    bad = json.dumps({**VALID, "urgency": "ASAP!!"})
    llm = FakeLLM(bad, json.dumps(VALID))
    _extract(llm)

    repair_prompt = llm.prompts[1]
    assert "urgency" in repair_prompt
    assert bad in repair_prompt
    assert MESSAGE in repair_prompt


def test_not_json_is_repaired() -> None:
    llm = FakeLLM("Sure! Here is the job: boiler repair in Leeds", json.dumps(VALID))
    result = _extract(llm)

    assert result.validated is True
    assert result.repair_attempts == 1


def test_repair_is_bounded() -> None:
    # The model never recovers: we must stop after max_repairs, not loop.
    llm = FakeLLM(*["not json"] * 10)
    result = _extract(llm, max_repairs=2)

    assert result.validated is False
    assert result.job is None
    assert result.repair_attempts == 2
    assert len(llm.prompts) == 3  # 1 initial + 2 repairs, never more
    assert result.last_error


def test_zero_repairs_means_one_call() -> None:
    llm = FakeLLM("not json", json.dumps(VALID))
    result = _extract(llm, max_repairs=0)

    assert result.validated is False
    assert len(llm.prompts) == 1


def test_negative_max_repairs_is_rejected() -> None:
    with pytest.raises(ValueError):
        _extract(FakeLLM(), max_repairs=-1)


def test_trusted_fields_from_the_model_are_rejected() -> None:
    # caller_number comes from Twilio metadata, never from the LLM (rule 4).
    smuggled = json.dumps({**VALID, "caller_number": "+447999999999"})
    llm = FakeLLM(smuggled, json.dumps(VALID))
    result = _extract(llm)

    assert result.repair_attempts == 1
    assert result.job is not None
    assert not hasattr(result.job, "caller_number")


def test_records_prompt_version_for_the_audit_row() -> None:
    result = _extract(FakeLLM(json.dumps(VALID)))

    assert result.prompt_version == "extract_v1"
