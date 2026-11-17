---
id: D-027
title: "Retention + erasure: raw/audit data redacted at 90 days, job records kept, on-request erase (#95)"
status: accepted
date: 2026-11-13
---

# D-027 — Retention + erasure: raw/audit data redacted at 90 days, job records kept, on-request erase (#95)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap for the *policy* (three constants), one-way for an already-redacted row —
  which is the point.

## Context

D-025 redacted outbound `to`/`body` at 30 days but deliberately left the wider
question open: `raw_events.payload`/`caller_number` and `llm_output_audits.raw_output` still carry
caller numbers and message text, held forever. The same question splits into two jobs — a
time-based schedule (how long may the *operational* logs keep personal data) and a request-based
erasure (the caller asks to be forgotten).

## Decision

- `raw_events.payload` and `raw_events.caller_number` are **redacted (blanked, not deleted) after
  90 days**, as is `llm_output_audits.raw_output`. 90 days is long enough to replay a failed
  extraction and debug, short enough to be defensible. The idempotency key, `source`, timestamps,
  status and attempt counts survive, so dedupe and metrics keep working.
- A reply still retryable (extraction never ran, or last failed) is skipped by the purge: blanking
  its body would turn a recoverable lead into an empty guaranteed dead-letter.
- `job_records` (including `raw_message`, the caller's exact words) and `human_edits` are **kept
  for as long as the caller is a customer**. They are the tradesperson's business record — the
  product, not an operational log — and keep the original wording for reviewing edits. A blanket
  purge would destroy the record of work done.
- **Erasure on request** (`just erase <number>`, E.164) clears one caller's number, message text
  and identifying extracted fields (`name`, `location`, `preferred_date`) across `raw_events`,
  `outbound_messages`, `job_records` and `llm_output_audits`, keeping the operational skeleton so
  counts stay coherent. The tradesperson's own corrections (`human_edits`) are not erased with the
  caller — they are the operator's action trail.

## Consequences

`db/retention.py` (`redact_raw_events`, `redact_llm_outputs`, `erase_person`);
`scripts/purge_old_data.py` now covers raw/audit on top of outbound; `scripts/erase_person.py` +
`just erase <number>`; scheduled alongside the other purge/retry commands.

## Source

#95; founder decision 2026-11-13.
