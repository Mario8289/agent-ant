---
id: D-026
title: "Support alerting via Slack incoming webhook (operator, not customer) (#94)"
status: accepted
date: 2026-11-13
---

# D-026 — Support alerting via Slack incoming webhook (operator, not customer) (#94)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap — remove the webhook URL and the notifier is a no-op.

## Context

D-023 and D-024 made failures *visible* on the dashboard but not *pushed*: the
founder would have to open the dashboard to notice a failed send or a dead-lettered extraction.
The dashboard is the tradesperson's surface; infra failures are the *operator's* job (provider
down, retry queue filling) and pushing them to the tradesperson would confuse him. The founder
asked where alerts land and split the channels himself: he wants system logs/alerts in Slack,
and will use WhatsApp (or in-app chat) for *client* conversations later.

## Decision

- Support alerts go to **Slack via an incoming webhook** (`SLACK_WEBHOOK_URL`, a `SecretStr`).
  Unset = no-op, so local dev stays quiet.
- Two alert types, both in background tasks / scheduled scripts (never the webhook hot path):
  an SMS send failure, and a dead-lettered extraction (needs manual filing).
- Alert text carries a SID/number, never a message body or caller number (rule 5), and points
  the operator at the dashboard. `post_to_slack` swallows all errors — alerting must never take
  down the thing it watches.
- Customer-facing conversation stays a *separate, later* product decision: WhatsApp or in-app
  chat, not Slack.

## Consequences

`apps/api/src/agent_ant_api/notify.py` (`post_to_slack`, `make_notifier`,
`notify_support`); `slack_webhook_url` on `Settings`; `SLACK_WEBHOOK_URL` in `.env.example`;
`just test-slack` (`scripts/test_slack.py`); wired into `sms.py` (send failure) and
`extraction.py` (dead-letter).

## Source

#94; founder decision 2026-11-13.
