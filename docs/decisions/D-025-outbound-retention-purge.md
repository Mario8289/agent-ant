---
id: D-025
title: "Retention purge: outbound personal fields redacted at 30 days; wider retention deferred (#34)"
status: accepted
date: 2026-11-13
---

# D-025 — Retention purge: outbound personal fields redacted at 30 days; wider retention deferred (#34)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap — a constant and a script. (The redaction itself is one-way for the row,
  which is the point.)

## Context

D-021 fixed the 30-day line for `outbound_messages.to`/`body` but left the purge
automation to #34. The wider question — how long to keep `raw_events.payload` and
`job_records.raw_message`, which also carry caller numbers and message bodies — is *not*
answered by D-021 and cannot be assumed to be 30 days.

## Decision

- `purge_personal_data` (`just purge`) clears `outbound_messages.to` and `body` (sets to `""`)
  once a row is older than 30 days, keeping the SID, status, error code and timestamps for
  aggregate metrics. Idempotent: already-redacted rows are skipped.
- The wider retention of `raw_events`, `job_records` and `llm_output_audits` is **deferred** to a
  separate founder decision (D-0xx): those tables are the business data itself — the job record
  is the product, not an operational log — so a blanket 30-day purge would destroy the record of
  work done.

## Consequences

`purge_personal_data` in `db/outbound_sms.py`; `scripts/purge_old_data.py` +
`just purge`; scheduled alongside the retry commands.

## Source

#34; D-021; founder decision 2026-11-13.
