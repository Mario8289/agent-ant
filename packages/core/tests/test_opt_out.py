"""Opt-out state: idempotent record and lookup (issue #72)."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agent_ant_core.db.models import OptOut
from agent_ant_core.db.opt_out import is_opted_out, record_opt_out

NUMBER = "+447000000000"


def test_not_opted_out_by_default(session: Session) -> None:
    assert is_opted_out(session, NUMBER) is False


def test_record_opt_out_is_idempotent(session: Session) -> None:
    record_opt_out(session, NUMBER)
    session.commit()
    record_opt_out(session, NUMBER)  # a duplicate STOP must not create a second row
    session.commit()

    assert is_opted_out(session, NUMBER) is True
    count = session.execute(select(func.count()).select_from(OptOut)).scalar_one()
    assert count == 1
