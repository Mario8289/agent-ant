import json

import pytest
from extract import JobExtraction, extract_job

MESSAGE = "hi its Sam, boiler has packed in, in Leeds LS6, really urgent, could do tomorrow"

VALID = {
    "name": "Sam",
    "job_type": "boiler repair",
    "location": "Leeds LS6",
    "urgency": "high",
    "preferred_date": "tomorrow",
}


class ScriptedLLM:
    """Returns queued replies in order and records every prompt it was given."""

    def __init__(self, *replies: str) -> None:
        self.replies = list(replies)
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.replies.pop(0)


def test_messy_text_becomes_a_validated_object() -> None:
    llm = ScriptedLLM(json.dumps(VALID))
    result = extract_job(llm, MESSAGE)

    assert result.validated is True
    assert result.repair_attempts == 0
    assert result.job == JobExtraction(**VALID)
    assert len(llm.prompts) == 1
    assert MESSAGE in llm.prompts[0]


def test_missing_fields_default_instead_of_failing() -> None:
    result = extract_job(ScriptedLLM('{"job_type": "leaking tap"}'), "got a leaky tap")

    assert result.validated is True
    assert result.job is not None
    assert result.job.urgency == "unknown"
    assert result.job.name is None


def test_code_fenced_json_is_accepted() -> None:
    result = extract_job(ScriptedLLM("```json\n" + json.dumps(VALID) + "\n```"), MESSAGE)

    assert result.validated is True
    assert result.repair_attempts == 0


def test_invalid_output_is_repaired() -> None:
    bad = json.dumps({**VALID, "urgency": "ASAP!!"})
    llm = ScriptedLLM(bad, json.dumps(VALID))
    result = extract_job(llm, MESSAGE)

    assert result.validated is True
    assert result.repair_attempts == 1
    assert result.job == JobExtraction(**VALID)
    assert result.raw_outputs == [bad, json.dumps(VALID)]


def test_repair_prompt_carries_the_error_and_previous_output() -> None:
    bad = json.dumps({**VALID, "urgency": "ASAP!!"})
    llm = ScriptedLLM(bad, json.dumps(VALID))
    extract_job(llm, MESSAGE)

    repair_prompt = llm.prompts[1]
    assert "urgency" in repair_prompt
    assert bad in repair_prompt
    assert MESSAGE in repair_prompt


def test_not_json_is_repaired() -> None:
    llm = ScriptedLLM("Sure! Here is the job: boiler repair in Leeds", json.dumps(VALID))
    result = extract_job(llm, MESSAGE)

    assert result.validated is True
    assert result.repair_attempts == 1


def test_repair_is_bounded() -> None:
    # The model never recovers: we must stop after max_repairs, not loop.
    llm = ScriptedLLM(*["not json"] * 10)
    result = extract_job(llm, MESSAGE, max_repairs=2)

    assert result.validated is False
    assert result.job is None
    assert result.repair_attempts == 2
    assert len(llm.prompts) == 3  # 1 initial + 2 repairs, never more
    assert result.last_error


def test_zero_repairs_means_one_call() -> None:
    llm = ScriptedLLM("not json", json.dumps(VALID))
    result = extract_job(llm, MESSAGE, max_repairs=0)

    assert result.validated is False
    assert len(llm.prompts) == 1


def test_negative_max_repairs_is_rejected() -> None:
    with pytest.raises(ValueError):
        extract_job(ScriptedLLM(), MESSAGE, max_repairs=-1)


def test_trusted_fields_from_the_model_are_rejected() -> None:
    # caller_number comes from Twilio metadata, never from the LLM (rule 4).
    smuggled = json.dumps({**VALID, "caller_number": "+447999999999"})
    llm = ScriptedLLM(smuggled, json.dumps(VALID))
    result = extract_job(llm, MESSAGE)

    assert result.repair_attempts == 1
    assert result.job is not None
    assert not hasattr(result.job, "caller_number")


def test_records_prompt_version_for_the_audit_row() -> None:
    result = extract_job(ScriptedLLM(json.dumps(VALID)), MESSAGE)

    assert result.prompt_version == "extract_v1"
