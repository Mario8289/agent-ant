"""The job-progress state machine (D-030): four states, moves as data, one ``transition()``.

``job_status`` (Lead / In work / Complete / Lost) is separate from the extraction-review
``status`` that ``approval.py`` manages. MVP moves are made by the trader; agents create leads
but do not move jobs. On hold is a flag on an ``in_progress`` job, not a state.
"""

from sqlalchemy.orm import Session

from agent_ant_core.db.models import JobEvent, JobRecord

# Allowed moves, as data so a new state is one edit rather than a code change (D-030).
ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "enquiry": frozenset({"in_progress", "lost"}),
    "in_progress": frozenset({"completed"}),
    "completed": frozenset(),
    "lost": frozenset(),
}


def transition(
    session: Session,
    job_id: int,
    to_status: str,
    *,
    actor: str,
    reason: str | None = None,
) -> JobRecord | None:
    """Move a job to ``to_status`` if the move is allowed, appending one ``job_events`` row.

    Returns the job, or ``None`` when the job is missing or the move is not allowed (in which
    case nothing is written). The caller owns the transaction and commits. Leaving
    ``in_progress`` clears the on-hold flag.
    """
    job = session.get(JobRecord, job_id)
    if job is None:
        return None
    from_status = job.job_status
    if to_status not in ALLOWED_TRANSITIONS.get(from_status, frozenset()):
        return None

    job.job_status = to_status
    if to_status != "in_progress":
        job.on_hold = False
    session.add(
        JobEvent(
            job_id=job.id,
            from_status=from_status,
            to_status=to_status,
            actor=actor,
            reason=reason,
        )
    )
    return job


def set_on_hold(session: Session, job_id: int, value: bool) -> JobRecord | None:
    """Set (or clear) the on-hold flag. Setting it requires an ``in_progress`` job.

    Returns the job, or ``None`` when the job is missing or ``value`` is true on a job that is
    not ``in_progress``. Clearing is always allowed (a no-op when already false).
    """
    job = session.get(JobRecord, job_id)
    if job is None:
        return None
    if value and job.job_status != "in_progress":
        return None
    job.on_hold = value
    return job
