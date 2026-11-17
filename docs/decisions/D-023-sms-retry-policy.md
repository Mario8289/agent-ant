---
id: D-023
title: "Retry policy: failed SMS sends retried up to 3 attempts, then dead-lettered (#34)"
status: accepted
date: 2026-11-13
---

# D-023 — Retry policy: failed SMS sends retried up to 3 attempts, then dead-lettered (#34)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap — `MAX_SEND_ATTEMPTS` is one constant.

## Context

#34 (hardening). A failed SMS send was recorded (D-021) but never retried, and
nothing surfaced it except a log line. The blocker to G0b is trust — Dad will not forward his
livelihood's calls to something that can silently drop a text — so a failed send must be visible
and recoverable.

## Decision

- A failed send (`status='failed'`) is retried up to **3 attempts** (including the first) via
  `just retry-sms`; each retry bumps `outbound_messages.attempts`.
- After the bound, it is **dead-lettered** (`status='dead'`) and listed on the dashboard's
  failure panel for manual handling.
- The retry is a command, not automatic — schedule it (cron / App Runner scheduled job) at
  deploy. The dashboard panel is the MVP "alert"; email/Slack alerting is deferred to a later
  #34 slice. Extraction failures are retried separately, also later.

## Consequences

`outbound_messages.attempts` (migration 0007), `retry_failed_sends` and
`list_failed_messages` in `db/outbound_sms.py`, `scripts/retry_sms.py` + `just retry-sms`, and a
dashboard failure panel.

## Source

#34; founder decision 2026-11-13; D-021.
