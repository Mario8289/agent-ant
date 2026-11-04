---
title: Hypothesis Table
status: draft
version: 0.2
last_updated: 2026-11-04
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
| **H8** | Extraction is accurate enough to be useful | Score against a hand-labelled golden set | ≥ agreed accuracy threshold on job_type + callback + urgency | Week 3 eval | — | untested |

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
- H8 accuracy threshold: set when the golden set is labelled, before scoring.
- H5: what evidence would count as "~10x"? Needs defining before the teardown.

## Change history

- **0.2 (2026-11-04)** — H6/H7/H8 added; H5 replaced ("unified beats fragmented" was
  contradicted by competitors already offering unified products); pass lines made numeric;
  vanity-metric list added.
- **0.1** — five assumptions, qualitative pass lines.
