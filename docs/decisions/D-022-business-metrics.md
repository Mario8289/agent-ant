---
id: D-022
title: "Business metrics frozen: capture rate, reply rate, jobs booked, edit rate (#30)"
status: accepted
date: 2026-11-13
---

# D-022 — Business metrics frozen: capture rate, reply rate, jobs booked, edit rate (#30)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap — the definitions are one module. Changing any of them after the first
  live read invalidates that read, so supersede instead (append a new entry).

## Context

#30 asked for "capture rate, reply rate, jobs booked, edit rate". docs/discovery/hypotheses.md's
definitions were deliberately loose ("missed calls that produced a stored record", "human edits
÷ AI-produced job records"). A metric must be frozen *before* it is read, or its line can be
moved after seeing results (Ries — the docs/discovery/hypotheses.md anti-pattern). D-021 made "texts sent"
queryable, so the reply-rate denominator can finally be real rather than "missed calls".

## Decision

freeze the exact counts, computed in `agent_ant_core/metrics.py`:
- **capture_rate** = `job_records ÷ voice_calls` — jobs captured per missed call. Every
  `job_records` row counts as captured (extraction wrote it), whatever its later status.
- **reply_rate** = `sms_replies ÷ outbound_messages` — replies per auto-text sent. Gates H6.
- **jobs_booked** = `count(job_records WHERE status='approved')` — a count, the money metric.
- **edit_rate** = `distinct jobs with ≥1 human_edit ÷ job_records` — corrections per AI job, the
  LLM-drift alarm.
- Each rate is `0.0` when its denominator is empty.

## Consequences

- Exposed on the dashboard (server-rendered, D-014) as counts plus percentages, e.g.
  "3 jobs / 10 missed calls (30%)".
- **H6's reply-rate threshold is still not frozen.** The issue's second box ("freeze after the
  first live week") is deferred: `reply_rate` is computed now, but no pass line exists until
  there is a live week to set it from.
- Accepted caveat: `capture_rate` counts every `job_records` row, and a reply with no missed
  call (a caller texting the number directly) still produces a job, so the ratio can exceed 1.0
  in theory. Harmless at MVP volume.

## Source

#30; docs/discovery/hypotheses.md metric definitions; Ries, *The Lean Startup* (2011), innovation accounting.
