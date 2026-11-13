"""Opt-out state: callers who texted STOP and must not receive auto-texts (#72).

The keyword decision is a product choice (D-019); this module only stores and reads the result.
It is a plain table keyed on the caller's number, not a flag on ``raw_events``, because an opt-out
is state that accumulates across events rather than a property of any one event.
"""

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from agent_ant_core.db.models import OptOut


def is_opted_out(session: Session, caller_number: str) -> bool:
    """True once this caller has opted out, so future auto-texts are suppressed."""
    return session.get(OptOut, caller_number) is not None


def record_opt_out(session: Session, caller_number: str) -> None:
    """Persist an opt-out idempotently.

    A caller texting STOP twice must not create two rows, and two concurrent retries must not
    race, so the insert uses ``ON CONFLICT DO NOTHING`` and lets the database decide (the same
    reasoning as ``idempotency.py``). The caller owns the transaction and commits.
    """
    statement = (
        insert(OptOut)
        .values(caller_number=caller_number)
        .on_conflict_do_nothing(index_elements=[OptOut.caller_number])
    )
    session.execute(statement)
