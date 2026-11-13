---
title: Hypothesis Table
status: draft
version: 0.4
last_updated: 2026-11-13
sources:
  - Ries — The Lean Startup (2011) — leap-of-faith, innovation accounting — verified
  - Fitzpatrick — The Mom Test (2013) — commitment currencies — verified
  - Thiel — Zero to One (2014) — 10x, beachhead — verified
  - Huyen — AI Engineering (2025) — HITL, evaluation — verified
---

# 01 — Hypothesis Table

## Purpose

Turn each leap-of-faith assumption into a falsifiable test with a pass line committed
**before** data arrives. Per **Ries**, this is innovation accounting: decide the pass/fail
line up front so results cannot be rationalised afterwards.

## Rules for using this table

1. **Freeze the pass line before the test starts.** Editing it afterwards invalidates the test.
2. **Record the actual result**, not a narrative about the result.
3. **A failed hypothesis is information.** Per Ries, that is validated learning.
4. Rows are append-only. If a hypothesis changes, add a new row and mark the old one superseded.

## Table

| ID | Hypothesis | Falsifiable test | Pass line (committed) | Evidence source | Result | Status |
|---|---|---|---|---|---|---|
| **H1** | Missed calls cost sole traders real jobs and money | 6 Mom Test interviews, past-behaviour questions only | ≥3 of 6 recall a **specific** missed call **and** a lost job | Doc 03 | — | untested |
| **H2** | Traders will let an AI assist with customer comms | Dad live in Week 4, HITL approve/edit | Dad approves or corrects ≥1 real job **unaided** | Week 4 log | — | untested |
| **H3** | They will pay a recurring subscription | Pricing conversation + deposit ask, post-prototype | ≥1 deposit or pre-order (cash currency, not verbal interest) | Doc 03 commitment row | — | untested |
| **H4** | The wedge creates pull for adjacent jobs | Observe Week 4–6 behaviour | Dad **asks** for invoicing/quoting next, unprompted | Week 6 write-up | — | untested |
| **H5** | Niche depth beats horizontal breadth | Competitor teardown + 10x comparison on one axis | A named axis where the product is demonstrably ~10x better for carpenters | Competitor notes in doc 00 §3 (pricing checked 2026-11-04) | — | untested |
| **H6** | **Callers reply to the auto-text** | Live missed calls in Weeks 4–6 | Reply rate ≥ threshold *(set after week 1 live, then freeze)* | Twilio logs | — | untested |
| **H7** | Design partners refer other tradespeople | Ask each interviewee for an intro | ≥2 actual introductions made (reputation currency) | Doc 03 | — | untested |
| **H8** | Extraction is accurate enough to be useful | Score against a hand-labelled golden set | job_type ≥ 0.80 and urgency ≥ 0.90 *(proposed — freeze before the first scored run)* | Week 3 eval | First scored run on `golden_v1` with exact match: `job_type` 7/20 (0.35), `urgency` 16/20 (0.80). Fails. The line was never frozen before this run (D-017) | **failed; superseded by H8a** |
| **H8a** | Extraction is accurate enough to be useful (replaces H8) | `job_type` scored by containment (answer within one word of the label), mean of 3 runs on the held-out `golden_v2` (40 messages), prompt `extract_v3` | job_type ≥ 0.80 and urgency ≥ 0.90 *(frozen 2026-11-13 by D-017, before the gated run)* | Week 3 eval; real evidence is the Week 4 edit rate | 2026-11-13, one gated run on `golden_v2` (3 passes of 40): `job_type` 36, 35, 35 /40 (mean 0.883), `urgency` 40/40 each (1.000). Passes the line. A synthetic smoke test; live edit rate still decides | **passed (smoke test)** |

## Metric definitions (avoid vanity metrics)

| Metric | Definition | Type |
|---|---|---|
| Capture rate | missed calls that produced a stored record ÷ total missed calls | actionable |
| **Reply rate** | missed calls where the caller replied ÷ auto-texts sent | actionable, gates H6 |
| Jobs recovered | jobs booked that would otherwise have been lost | actionable, the money metric |
| Edit rate | human edits ÷ AI-produced job records | actionable, doubles as LLM drift alarm (Huyen) |
| Deposits | cash committed | actionable, gates H3 |
| Total calls logged | — | **vanity — do not report as progress** |

## Anti-patterns

- ⚠️ **Moving the pass line after seeing results** (Ries) — the most common way this table gets gamed.
- ⚠️ **Reporting activity as validation** (Ries) — calls logged, messages sent, features shipped.
- ⚠️ **Counting compliments as commitment** (Fitzpatrick) — only time, reputation or cash count.
- ⚠️ **Testing H3 with "would you pay?"** (Fitzpatrick) — a hypothetical, not evidence. Ask for a deposit.

## Open questions

- H6 reply-rate threshold: propose after the first live week, then freeze.
- H8a accuracy threshold: job_type ≥ 0.80, urgency ≥ 0.90 in `evals/suites/scoring.py`, frozen
  by D-017 on 2026-11-13. "callback" was a stale field name — the
  current extraction schema has no callback field, so the gate is job_type + urgency.
- H5: what evidence would count as "~10x"? Needs defining before the teardown.

## Change history

- **0.4 (2026-11-13)** — H8a gated run recorded: passed. H8 result recorded (failed, exact match, first run) and superseded by
  H8a, which adds the containment metric, the held-out set and the mean of three runs (D-017).
- **0.3 (2026-11-09)** — H8 pass line made concrete (job_type ≥ 0.80, urgency ≥ 0.90), and the
  stale "callback" field dropped in favour of the actual extraction fields.
- **0.2 (2026-11-04)** — H6/H7/H8 added; H5 replaced ("unified beats fragmented" was
  contradicted by competitors already offering unified products); pass lines made numeric;
  vanity-metric list added.
- **0.1** — five assumptions, qualitative pass lines.
