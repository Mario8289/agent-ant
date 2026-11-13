"""Re-attempt failed SMS sends and dead-letter those that exhaust their retries (#34).

Run manually or on a schedule (``just retry-sms``). A send that failed at the Twilio boundary has
``status='failed'`` and no SID; this re-sends each one up to ``MAX_SEND_ATTEMPTS`` times and moves
the ones that still fail to ``status='dead'`` so the dashboard's failure panel can't miss them. A
send that dead-letters here also raises a Slack support alert (#96), so the operator learns about
it without opening the dashboard.
"""

import sys

from agent_ant_api.sms import alert_dead_letter, get_sms_sender
from agent_ant_core.config import get_settings
from agent_ant_core.db.models import OutboundMessage
from agent_ant_core.db.outbound_sms import retry_failed_sends
from agent_ant_core.db.session import get_sessionmaker


def main() -> int:
    settings = get_settings()
    sender = get_sms_sender(settings)
    if sender is None:
        print("Twilio is not configured; nothing to retry.", file=sys.stderr)
        return 2

    with get_sessionmaker()() as session:

        def on_dead_letter(message: OutboundMessage) -> None:
            alert_dead_letter(session, message)

        retried = retry_failed_sends(session, sender, on_dead_letter=on_dead_letter)
        session.commit()

    print(f"retried {retried} failed send(s); the rest were left failed or dead-lettered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
