"""#60 Spike 4: messy text -> validated object, with a bounded repair loop.

Never trust raw model text (Huyen). The model's reply is parsed and validated against a
Pydantic model; if that fails, the validation errors are fed back for a limited number of
repair attempts. When the cap is reached the result is "not validated" and the caller flags
the message for a human. It never raises, never loops forever, and never passes unvalidated
data on.

The LLM is a one-method interface so the loop can be tested deterministically with a scripted
fake: no API key, no cost, no customer data. That proves the loop, not any real model.
"""

from pathlib import Path
from string import Template
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, ValidationError

PROMPTS = Path(__file__).parent / "prompts"
EXTRACT_PROMPT = "extract_v1"
REPAIR_PROMPT = "repair_v1"
DEFAULT_MAX_REPAIRS = 2


class LLM(Protocol):
    def complete(self, prompt: str) -> str: ...


class JobExtraction(BaseModel):
    """Only the LLM-extractable fields from docs/05.

    `caller_number` and timestamps are trusted fields from Twilio metadata, never from the
    model, so `extra="forbid"` makes a reply that includes them invalid.
    """

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    job_type: str | None = None
    location: str | None = None
    urgency: Literal["low", "medium", "high", "unknown"] = "unknown"
    preferred_date: str | None = None


class ExtractionResult(BaseModel):
    """Maps onto LLMOutputAudit: prompt version, raw output, validated, repair attempts."""

    job: JobExtraction | None
    validated: bool
    repair_attempts: int
    prompt_version: str
    raw_outputs: list[str]
    last_error: str | None = None


def load_prompt(name: str) -> Template:
    return Template((PROMPTS / f"{name}.md").read_text())


def strip_code_fence(text: str) -> str:
    """Models often wrap JSON in ```json fences even when told not to."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.removesuffix("```")
    return text.strip()


def describe_errors(exc: ValidationError) -> str:
    """One line per problem, without echoing the offending input back."""
    return "\n".join(
        f"- {'.'.join(str(p) for p in err['loc']) or 'JSON'}: {err['msg']}"
        for err in exc.errors(include_url=False, include_input=False, include_context=False)
    )


def extract_job(llm: LLM, message: str, max_repairs: int = DEFAULT_MAX_REPAIRS) -> ExtractionResult:
    """Ask the model, validate, and repair up to `max_repairs` times.

    Total model calls are at most 1 + max_repairs.
    """
    if max_repairs < 0:
        raise ValueError("max_repairs must be >= 0")

    raw = llm.complete(load_prompt(EXTRACT_PROMPT).substitute(message=message))
    raw_outputs = [raw]
    repair_attempts = 0

    while True:
        try:
            job = JobExtraction.model_validate_json(strip_code_fence(raw))
        except ValidationError as exc:
            error = describe_errors(exc)
        else:
            return ExtractionResult(
                job=job,
                validated=True,
                repair_attempts=repair_attempts,
                prompt_version=EXTRACT_PROMPT,
                raw_outputs=raw_outputs,
            )

        if repair_attempts >= max_repairs:
            return ExtractionResult(
                job=None,
                validated=False,
                repair_attempts=repair_attempts,
                prompt_version=EXTRACT_PROMPT,
                raw_outputs=raw_outputs,
                last_error=error,
            )

        repair_attempts += 1
        raw = llm.complete(
            load_prompt(REPAIR_PROMPT).substitute(
                message=message, previous_output=raw, errors=error
            )
        )
        raw_outputs.append(raw)
