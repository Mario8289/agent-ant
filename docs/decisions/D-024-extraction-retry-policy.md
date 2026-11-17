---
id: D-024
title: "Retry policy: failed extractions retried up to 3 attempts, then dead-lettered (#34)"
status: accepted
date: 2026-11-13
---

# D-024 — Retry policy: failed extractions retried up to 3 attempts, then dead-lettered (#34)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap — `MAX_EXTRACTION_ATTEMPTS` is one constant.

## Context

#34 (hardening). A failed extraction — invalid output after its bounded repairs, or a
raised provider call — was swallowed by the background task: the invalid case left only an audit
row, the raised case left nothing but a log line. Neither was ever retried, and an extraction
failure is the higher-stakes gap of the two (a lost *lead*, versus a lost auto-text). Same trust
argument as D-023, now for the job itself.

## Decision

- `raw_events` gains `extraction_attempts` (default 0) and `extraction_status` (`done` /
  `failed` / `dead`; `NULL` = never attempted). Voice calls are never extracted, so they stay
  0 / `NULL`.
- Every attempt — the background task's first run included — bumps `extraction_attempts` and
  records `done` (a job was captured) or `failed` (invalid, or the provider raised). A raised
  call is rolled back and re-marked `failed` in a fresh transaction, so an outage surfaces as a
  retryable row instead of vanishing.
- `retry_failed_extractions` (`just retry-extractions`) re-runs extraction over every reply that
  is not `done` and under `MAX_EXTRACTION_ATTEMPTS` (3); a reply still `failed` at the bound is
  promoted to `dead` and shown on the dashboard's failure panel.
- Idempotency is unchanged: `persist_job_record` (`INSERT … ON CONFLICT DO NOTHING`) means a
  concurrent retry cannot create a second job.

## Consequences

migration 0008; `db/extraction.py` (`candidate_replies`,
`list_failed_extractions`); `extraction.py` (`_extract_one`, `retry_failed_extractions`);
`scripts/retry_extractions.py` + `just retry-extractions`; the dashboard "failed extractions"
panel.

## Source

#34; D-023 (the SMS analogue); founder decision 2026-11-13.
