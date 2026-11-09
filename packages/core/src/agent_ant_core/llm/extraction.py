"""Structured extraction with bounded repair (issue #22).

Never trust raw model text (Huyen): the reply is parsed and validated against a Pydantic model.
On failure the validation errors are fed back for a bounded number of repair attempts, after
which the result is flagged invalid for a human. It never raises on bad output, never loops
forever, and never passes unvalidated data on.

Trusted fields (``caller_number``, timestamps) are never extracted: the model is forbidden from
returning them, and ``extra="forbid"`` makes a reply that smuggles them invalid (rule 4).
"""

from string import Template
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from agent_ant_core.llm.client import LLM

DEFAULT_MAX_REPAIRS = 2


class JobExtraction(BaseModel):
    """Only the LLM-extractable fields from docs/05.

    ``caller_number`` and timestamps are trusted fields from Twilio metadata, never from the
    model, so ``extra="forbid"`` makes a reply that includes them invalid.
    """

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    job_type: str | None = None
    location: str | None = None
    urgency: Literal["low", "medium", "high", "unknown"] = "unknown"
    preferred_date: str | None = None


class ExtractionResult(BaseModel):
    """What one extraction attempt produced, for the audit trail.

    Maps onto ``LLMOutputAudit``: ``prompt_version``, ``raw_outputs``, ``validated`` and
    ``repair_attempts`` are all here so the caller can record the row without reaching into
    provider internals.
    """

    job: JobExtraction | None
    validated: bool
    repair_attempts: int
    prompt_version: str
    raw_outputs: list[str]
    last_error: str | None = None


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


def extract_job(
    llm: LLM,
    message: str,
    *,
    extract_prompt: str,
    repair_prompt: str,
    prompt_version: str,
    max_repairs: int = DEFAULT_MAX_REPAIRS,
) -> ExtractionResult:
    """Ask the model, validate, and repair up to ``max_repairs`` times.

    Total model calls are at most ``1 + max_repairs``. ``extract_prompt`` and ``repair_prompt``
    are ``string.Template`` text carrying ``$message`` (and, for repair, ``$previous_output``
    and ``$errors``). They are passed in, not loaded here, so core stays prompt- and
    agent-agnostic while the agent keeps its versioned prompt files.
    """
    if max_repairs < 0:
        raise ValueError("max_repairs must be >= 0")

    raw = llm.complete(Template(extract_prompt).substitute(message=message))
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
                prompt_version=prompt_version,
                raw_outputs=raw_outputs,
            )

        if repair_attempts >= max_repairs:
            return ExtractionResult(
                job=None,
                validated=False,
                repair_attempts=repair_attempts,
                prompt_version=prompt_version,
                raw_outputs=raw_outputs,
                last_error=error,
            )

        repair_attempts += 1
        raw = llm.complete(
            Template(repair_prompt).substitute(message=message, previous_output=raw, errors=error)
        )
        raw_outputs.append(raw)
