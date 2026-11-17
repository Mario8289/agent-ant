---
id: D-013
title: "`job_records` table + background extraction; the approval interrupt stays Week 4"
status: accepted
date: 2026-11-09
---

# D-013 — `job_records` table + background extraction; the approval interrupt stays Week 4

- **Date:** 2026-11-09
- **Status:** accepted
- **Reversible?** cheap — tables are new; the background-task wiring is a small seam.

## Context

With #22/#23/#24 merged, the pieces existed separately but nothing joined them:
there was no `job_records` table, the graph was not connected to the webhook, and no audit row
was ever written. Week 2's "done when" (a reply becomes a validated record *with an audit row*)
was therefore still unmet.

## Decision

Add a `job_records` table mirroring the `JobRecord` contract, with a unique
`idempotency_key` (the reply's `MessageSid`) and a `raw_event_id` foreign key. The SMS-reply
webhook schedules a background task (`extract_reply`) that runs `process_reply`: extract, then
persist a `captured` job plus an audit row (or the audit row alone on failure). The
`llm_output_audits.job_id` foreign key deferred in D-012 is now added. The LangGraph
`interrupt()` approval path is deliberately not wired: that is the Week 4 dashboard, so a valid
extraction is stored `captured` and waits.

## Consequences

A synthetic reply now becomes a captured job plus an audit row end to end.
The Bedrock adapter is still absent (`get_llm` returns None), so extraction is skipped until
credentials exist (`docs/runbooks/manual-steps.md`). `build_agent` in `graph.py` remains for the Week 4 approval path.

## Source

[design doc](../design/design-doc.md) §Schema;
[execution plan](../planning/execution-plan.md) Week 2 "done when"; D-008, D-012
