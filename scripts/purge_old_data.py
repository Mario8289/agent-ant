"""Redact personal data past the 30-day retention window (D-021, issue #34).

Run manually or on a schedule (``just purge``). Outbound ``to`` and ``body`` fields older than 30
days are cleared; the SID, status and timestamps stay so aggregate metrics remain correct. The
wider retention question (``raw_events.payload``, ``job_records.raw_message``) is a separate
founder decision — those tables are the business data itself, so they are not touched here.
"""

from agent_ant_core.db.outbound_sms import purge_personal_data
from agent_ant_core.db.session import get_sessionmaker


def main() -> int:
    with get_sessionmaker()() as session:
        purged = purge_personal_data(session)
        session.commit()

    print(f"redacted {purged} outbound message(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
