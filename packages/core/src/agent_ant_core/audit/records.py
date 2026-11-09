"""Recording helpers for the audit trail (R6).

Week 2, issue #24. Every extraction and every human correction is written here so quality drift
is measured, not guessed. The functions are plain: they take the caller's session and do not
commit, matching ``db/idempotency.py`` — the caller owns the transaction boundary.
"""

from sqlalchemy.orm import Session

from agent_ant_core.db.models import HumanEdit, LLMOutputAudit

EditDiff = dict[str, dict[str, str | None]]


def record_llm_output(
    session: Session,
    *,
    raw_event_id: int,
    model: str,
    prompt_version: str,
    raw_output: str,
    validated: bool,
    repair_attempts: int = 0,
    job_id: int | None = None,
) -> int:
    """Persist one extraction attempt and return its audit id.

    ``validated`` is whether the output satisfied the Pydantic schema; an invalid attempt is
    recorded too, so the failure rate is visible rather than dropped. ``job_id`` stays null
    until the ``job_records`` table exists (#23).
    """
    row = LLMOutputAudit(
        raw_event_id=raw_event_id,
        job_id=job_id,
        model=model,
        prompt_version=prompt_version,
        raw_output=raw_output,
        validated=validated,
        repair_attempts=repair_attempts,
    )
    session.add(row)
    session.flush()  # populate row.id without committing; the caller owns the commit
    return row.id


def record_human_edit(
    session: Session,
    *,
    llm_output_id: int,
    edit_diff: EditDiff,
) -> int:
    """Persist one human correction to an extraction and return its edit id.

    ``edit_diff`` maps each changed field to its before/after values; fields the human left
    alone are omitted, so the edit rate counts real corrections rather than a full-field echo.
    """
    row = HumanEdit(llm_output_id=llm_output_id, edit_diff=edit_diff)
    session.add(row)
    session.flush()
    return row.id
