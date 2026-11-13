"""Redact personal data past its retention window (D-021/D-025/D-027, issues #34/#95).

Run manually or on a schedule (``just purge``).

- ``outbound_messages.to``/``body``: redacted after 30 days (D-021, D-025).
- ``raw_events.payload``/``caller_number`` and ``llm_output_audits.raw_output``: redacted after
  90 days (D-027). ``job_records`` and ``human_edits`` are the business record and are kept.
"""

from agent_ant_core.db.outbound_sms import purge_personal_data
from agent_ant_core.db.retention import redact_llm_outputs, redact_raw_events
from agent_ant_core.db.session import get_sessionmaker


def main() -> int:
    with get_sessionmaker()() as session:
        outbound = purge_personal_data(session)
        raw_events = redact_raw_events(session)
        audits = redact_llm_outputs(session)
        session.commit()

    print(
        f"redacted {outbound} outbound message(s), {raw_events} raw event(s), {audits} audit row(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
