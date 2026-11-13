"""Send one test alert to the configured Slack webhook (issue #94).

Run ``just test-slack`` to confirm the pipe works end to end before real traffic. Posts a single
line to the channel; if no webhook is configured it exits non-zero so the check is explicit.
"""

import sys

from agent_ant_api.notify import notify_support
from agent_ant_core.config import get_settings


def main() -> int:
    settings = get_settings()
    if settings.slack_webhook_url is None:
        print("SLACK_WEBHOOK_URL is not set — nothing to test.", file=sys.stderr)
        return 2

    notify_support("agent-ant test alert: the Slack webhook is wired up.")
    print("test alert sent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
