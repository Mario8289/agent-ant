"""Turn a stored reply into a persisted job record plus an audit row (Week 2 integration).

This is the "does the work" step the webhook hands off to: run extraction on the reply body and
persist the outcome. The tradesperson's approval (the ``interrupt()`` in ``graph.py``) is a later
week; here a valid extraction is stored as ``captured`` and waits for review, and an invalid one
is recorded in the audit table only.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from agent_ant_core.audit.records import record_llm_output
from agent_ant_core.db.jobs import persist_job_record
from agent_ant_core.llm import LLM, extract_job
from agent_ant_missed_call.prompts import (
    EXTRACT_PROMPT_VERSION,
    REPAIR_PROMPT_VERSION,
    load_prompt,
)


def process_reply(
    session: Session,
    llm: LLM,
    *,
    raw_event_id: int,
    idempotency_key: str,
    caller_number: str,
    received_at: datetime,
    message: str,
    model: str,
    max_repairs: int = 2,
) -> int | None:
    """Extract a job from a reply and persist the job record plus an audit row.

    Returns the new ``job_records`` id when a valid job was captured, else ``None`` (extraction
    failed and only the audit row was written). Never raises on bad LLM output: a failed
    extraction is recorded in the audit table, not propagated. The caller owns the transaction
    and must commit.
    """
    result = extract_job(
        llm,
        message,
        extract_prompt=load_prompt(EXTRACT_PROMPT_VERSION),
        repair_prompt=load_prompt(REPAIR_PROMPT_VERSION),
        prompt_version=EXTRACT_PROMPT_VERSION,
        max_repairs=max_repairs,
    )

    job_id = None
    if result.job is not None:
        job_id = persist_job_record(
            session,
            raw_event_id=raw_event_id,
            idempotency_key=idempotency_key,
            caller_number=caller_number,
            received_at=received_at,
            raw_message=message,
            job=result.job,
            status="captured",
        )

    # The final raw output is what determined the outcome, so it is the one audited.
    record_llm_output(
        session,
        raw_event_id=raw_event_id,
        job_id=job_id,
        model=model,
        prompt_version=result.prompt_version,
        raw_output=result.raw_outputs[-1],
        validated=result.validated,
        repair_attempts=result.repair_attempts,
    )
    return job_id
