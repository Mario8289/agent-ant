---
id: D-012
title: "Audit trail: two tables, `job_id` deferred"
status: accepted
date: 2026-11-09
---

# D-012 — Audit trail: two tables, `job_id` deferred

- **Date:** 2026-11-09
- **Status:** accepted
- **Reversible?** cheap — tables are new and empty.

## Context

R6 (silent LLM drift) needs every extraction and correction logged (#24).
The schema sketch in the design doc shows a single `LLMOutputAudit` model with `human_edited` and
`edit_diff` inline, and a `job_id` — but the `job_records` table it points at does not exist
yet (that is #23).

## Decision

Two tables. `llm_output_audits` is an immutable snapshot keyed to
`raw_events.id` (which exists today) with a nullable `job_id` whose foreign key is added in
#23. `human_edits` holds one row per correction, linked to `llm_output_audits.id`, with the
diff as JSONB (`field -> {"before", "after"}`). `human_edited` is derived from a
`human_edits` row existing, not stored. `edit_diff` is JSONB, not a string, so the edit rate
is queryable.

## Consequences

The audit is testable and useful now, before any job table exists.
Diverges from the single-model sketch in the design doc (updated in place). `job_id` gains a foreign
key in a later migration, after #23 creates `job_records`.

## Source

[design doc](../design/design-doc.md) R6; issue #24
