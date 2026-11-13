"""Support alerting to Slack (issue #94).

A failed SMS send or a dead-lettered extraction needs a human, and the human is the operator, not
the tradesperson — so these alerts go to *you* via a Slack incoming webhook, not to the customer
and not to the dashboard. The customer-facing channel (WhatsApp / in-app chat) is a separate,
later product decision.

The webhook is a secret (anyone who holds it can post to the channel), so it lives in settings as
a ``SecretStr`` and is never logged. Alerts fire in background tasks and scheduled scripts, never
in the webhook's hot path, so a slow or failing Slack call cannot affect request handling — and
the post itself swallows all errors: alerting must never take down the thing it is watching.
"""

import json
import logging
import urllib.error
import urllib.request
from collections.abc import Callable

from agent_ant_core.config import get_settings

logger = logging.getLogger(__name__)

SLACK_TIMEOUT_SECONDS = 5

# Slack's incoming webhook accepts a simple {"text": ...} JSON body. The URL is the one Slack
# hands you when you add an Incoming Webhook to a channel (hosted under hooks.slack.com).
_CONTENT_TYPE = "application/json"


def post_to_slack(webhook_url: str, text: str, *, timeout: int = SLACK_TIMEOUT_SECONDS) -> None:
    """POST one line of text to a Slack incoming webhook. Never raises.

    Kept free of settings and side effects so it is testable against a fake URL; ``notify_support``
    is the thin wrapper that reads the configured webhook.
    """
    request = urllib.request.Request(
        webhook_url,
        data=json.dumps({"text": text}).encode("utf-8"),
        headers={"Content-Type": _CONTENT_TYPE},
        method="POST",
    )
    try:
        urllib.request.urlopen(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        # Slack answers a bad webhook with an HTTP status plus a JSON body ({"error": ...}) that
        # names the real problem. Surface both; allowing this in a log is fine because the body
        # carries no secret and the URL is never echoed.
        reason = exc.read().decode("utf-8", errors="replace")
        logger.warning("slack webhook rejected the alert: HTTP %s %s", exc.code, reason)
    except Exception:
        # Alerting is best-effort by design: a Slack outage must not break the send/extraction
        # path. Log at warning so a misconfigured webhook is still diagnosable.
        logger.exception("slack alert could not be delivered")


def _noop(_text: str) -> None:
    return None


def make_notifier(webhook_url: str | None) -> Callable[[str], None]:
    """Return a notifier bound to ``webhook_url``, or a no-op when it is unset.

    Split out so a call site can build a notifier from an already-resolved setting and tests can
    inject one without touching the process-wide settings singleton.
    """
    if webhook_url:
        return lambda text: post_to_slack(webhook_url, text)
    return _noop


def notify_support(text: str) -> None:
    """Post a support alert to Slack, if a webhook is configured. Never raises."""
    webhook = get_settings().slack_webhook_url
    if webhook is None:
        return
    post_to_slack(webhook.get_secret_value(), text)
