"""Erase one caller's personal data across every table (D-027, issue #95).

Run ``just erase <number>`` (E.164, e.g. ``+447000000000``) to honour a right-to-erasure request.
The caller's number, message text and extracted name/location are cleared; operational fields
(status, timestamps, job type, urgency) stay so metrics remain coherent. The caller's own
corrections (``human_edits``) are the operator's action trail and are not touched.
"""

import sys

from agent_ant_core.db.retention import erase_person
from agent_ant_core.db.session import get_sessionmaker


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: just erase <number>", file=sys.stderr)
        return 2

    number = argv[1]
    with get_sessionmaker()() as session:
        counts = erase_person(session, number)
        session.commit()

    detail = ", ".join(f"{table}={n}" for table, n in counts.items())
    print(f"erased {number}: {detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
