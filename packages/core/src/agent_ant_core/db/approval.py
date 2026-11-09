"""Human approval of captured jobs (HITL — rule 6, D-006).

Nothing counts as confirmed without a human. These helpers apply the tradesperson's decision to
a captured job: approve, reject, or edit (apply corrections, write the ``human_edits`` diff, and
approve). They never commit — the caller owns the transaction, matching ``idempotency.py``.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ant_core.audit.records import record_human_edit
from agent_ant_core.db.models import JobRecord, LLMOutputAudit

# The extracted fields a human may correct. Trusted fields (caller_number, timestamps) are not.
EDITABLE_FIELDS = ("name", "job_type", "location", "urgency", "preferred_date")


def list_captured_jobs(session: Session) -> list[JobRecord]:
    """Jobs awaiting a human decision, oldest first."""
    return list(
        session.execute(
            select(JobRecord)
            .where(JobRecord.status == "captured")
            .order_by(JobRecord.received_at.asc(), JobRecord.id.asc())
        ).scalars()
    )


def _transition(session: Session, job_id: int, status: str) -> JobRecord | None:
    """Move a captured job to ``status``. Returns the job, or None if absent or already decided."""
    job = session.get(JobRecord, job_id)
    if job is None or job.status != "captured":
        return None
    job.status = status
    return job


def approve_job(session: Session, job_id: int) -> JobRecord | None:
    """Approve a captured job as-is."""
    return _transition(session, job_id, "approved")


def reject_job(session: Session, job_id: int) -> JobRecord | None:
    """Reject a captured job (not a real job after all)."""
    return _transition(session, job_id, "rejected")


def edit_job(session: Session, job_id: int, edits: dict[str, str | None]) -> JobRecord | None:
    """Apply corrections to a captured job, record the diff, and approve.

    ``edits`` maps editable field names to their corrected values; fields left out are untouched.
    Only fields that actually changed are written to ``human_edits``, so the edit rate counts
    real corrections rather than a full-field echo (R6). The human edit is linked to the audit
    row that produced the job; if there is none, the edit is applied but not logged.
    """
    job = session.get(JobRecord, job_id)
    if job is None or job.status != "captured":
        return None

    diff: dict[str, dict[str, str | None]] = {}
    for field in EDITABLE_FIELDS:
        if field not in edits:
            continue
        before = getattr(job, field)
        after = edits[field]
        if before != after:
            diff[field] = {"before": before, "after": after}
            setattr(job, field, after)

    if diff:
        audit = session.execute(
            select(LLMOutputAudit).where(LLMOutputAudit.job_id == job_id)
        ).scalar_one_or_none()
        if audit is not None:
            record_human_edit(session, llm_output_id=audit.id, edit_diff=diff)

    job.status = "approved"
    return job
