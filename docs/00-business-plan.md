---
title: Business Plan & 6-Week Prototype
status: draft
version: 0.2
last_updated: 2026-11-04
sources:
  - Fitzpatrick — The Mom Test ⚠️ TO CHECK
  - Ries — The Lean Startup ⚠️ TO CHECK
  - Thiel — Zero to One ⚠️ TO CHECK
  - Huyen — AI Engineering (agent autonomy limits) ⚠️ TO CHECK
---

# 00 — Business Plan & 6-Week Prototype

## Purpose

One-page thesis for a vertical AI assistant for sole traders, plus a 6-week sprint that
tests the riskiest assumptions with the least build effort. This document covers business
doctrine only; architecture lives in [05-architecture-and-schema.md](./05-architecture-and-schema.md).

## 1. Thesis

**Product:** a voice/text back-office assistant for sole traders.
**Wedge (v0):** missed call → auto-text → structured job record → human approval.
**Not v0:** invoicing, payments, accounting, real-time voice, multi-agent orchestration.

**Why this wedge:** a missed call is a live, high-frequency, monetisable loss. It is
demoable in minutes and avoids financial compliance. Invoice-chasing is deferred until
the wedge has earned trust.

## 2. Leap-of-faith assumptions

Per **Ries**, a startup rests on assumptions that, if false, invalidate the business.
Each is turned into a falsifiable hypothesis in
[01-hypothesis-table.md](./01-hypothesis-table.md). Success metrics are committed
**before** data is collected, per Ries's *innovation accounting*, so results cannot be
rationalised afterwards.

| ID | Assumption |
|---|---|
| H1 | Missed calls cost sole traders real jobs and money |
| H2 | Traders will let an AI assist with customer communication |
| H3 | They will pay a recurring subscription |
| H4 | The missed-call wedge creates pull for adjacent jobs (invoicing, quoting) |
| H5 | Niche depth beats horizontal breadth (replaces "unified beats fragmented") |
| H6 | **Callers actually reply to the auto-text** — the entire value chain depends on this |
| H7 | Design partners refer other tradespeople (early growth signal) |

> ⚠️ **Anti-pattern (Ries):** treating a polished plan as progress. If a hypothesis has no
> falsifying test, it is decoration, not a plan.

## 3. Competitors — ⚠️ TO CHECK (all pricing unverified)

| Player | Claim | Why it matters |
|---|---|---|
| VioTrade | All-in-one voice + quotes + invoices + jobs, ~£20/mo flat | Already "unified" — kills the old H5 |
| Tradehand | Answers + quotes + books + chases, from ~£25/mo | Full-pipeline positioning |
| MyTradeBuddy | Enquiry → qualified → chased → booked | Same pipeline claim |
| HeyItsClara / Rosie AI / Down To Earth AI | AI receptionist / message taking | Crowded at the answering layer |
| Tradify, ServiceM8, Fergus, Jobber | Job management, per-user pricing, little/no AI | Incumbents, differentiation window |

**Implication (Thiel):** "all failed companies are the same: they failed to escape
competition" ⚠️ TO CHECK. "UK tradespeople" is already contested, so the beachhead must be
narrower — **carpenters/joiners**, or one region, or one job type.

**Differentiation must be ~10x on one axis (Thiel), not a feature list.** Candidates:
carpentry-specific quoting using SKU/margin data; regional trust density.

> ⚠️ **Anti-pattern (Thiel):** competing as "VioTrade plus one more feature". That is
> one-to-n, not zero-to-one.

## 4. Discovery

Script: [02-mom-test-script-dad.md](./02-mom-test-script-dad.md).
Capture: [03-requirements-capture-sheet.md](./03-requirements-capture-sheet.md).

Per **Fitzpatrick**, three rules: talk about their life not your idea; ask about specifics
in the past not future opinions; talk less, listen more. Real signal is commitment in one
of three currencies — **time, reputation, cash**.

> ⚠️ **Anti-pattern (Fitzpatrick):** pitching during discovery. Describing the app
> contaminates the data. "Compliments are the fool's gold of customer learning" ⚠️ TO CHECK.

## 5. MVP definition

Per **Ries**, the MVP is the fastest path through Build-Measure-Learn with minimum effort —
built to test hypotheses, not to be polished.

> **MVP = a Twilio number that auto-texts a missed caller from a fixed template, captures
> the reply, and files a structured job record that Dad approves or edits.**

**Deliberate autonomy limit (Huyen):** the AI **never** writes free-text messages to
customers. Customer-facing SMS is a fixed template. AI output goes to Dad only. This caps
the blast radius of hallucination while H2 and H6 are still unproven.

**Actionable metrics only (Ries):**
- missed calls captured / total missed calls
- **caller reply rate** (H6)
- jobs booked from captured calls
- human edits per job (extraction quality + drift alarm)
- deposits / pre-orders (H3)

> ⚠️ **Anti-pattern (Ries):** vanity metrics. "Total calls logged" feels good and tests nothing.

## 6. Pre-sprint gates (run BEFORE any build hours)

Moved ahead of the sprint in v0.2 — previously the stack skeleton was built before the
problem was validated, which risked spending build hours on an unproven pain.

| Gate | Test | Pass line |
|---|---|---|
| **G0a — Discovery** | 6 Mom Test interviews | ≥3 of 6 cite a *specific* missed call and a lost job |
| **G0b — Carrier forwarding** ⚠️ TO CHECK | Forward Dad's unanswered calls to a Twilio number, caller ID preserved | Works on his real mobile plan |
| **G0c — Precursor skills** | Ready Check in doc 05 | All 5 items pass |

If G0a fails, do not build. Reconsider the wedge or the segment. Per Ries this is validated
learning, not failure. If G0b fails, the telephony design must change before any code.

## 7. 6-week sprint (~14 hrs/week)

| Week | Focus | Deliverable | Hypothesis |
|---|---|---|---|
| 1 | Twilio → FastAPI webhook; fixed-template auto-SMS; store raw reply | Missed call triggers a text; reply persisted | H6 |
| 2 | Extraction: reply → structured job record (Pydantic-validated) | Messy SMS becomes a clean record | H6 |
| 3 | Label a golden set of real messages; measure extraction accuracy | Accuracy score vs. threshold | H6, quality |
| 4 | Minimal dashboard + **HITL approve/edit**; **Dad goes live, text-only** | Dad approves/corrects real jobs unaided | H2 |
| 5 | Optional voicemail-to-text (async, not real-time). Otherwise harden + measure | More capture coverage, or better metrics | H2, H6 |
| 6 | Live measurement, pricing conversation, referral ask, write-up | Recovered jobs, deposit signal, intros | H3, H4, H7 |

**Changes from v0.1:** Dad goes live in **Week 4** instead of Week 6 (three weeks of real
data instead of one — Ries: shorten the loop). **Real-time voice moved post-Week 6**; no
hypothesis requires it and it was the highest-risk component.

## 8. Kill / continue gates

| When | Gate | If failed |
|---|---|---|
| Pre-sprint | G0a discovery, G0b forwarding | Stop; re-segment or redesign telephony |
| End W3 | Extraction accuracy ≥ agreed threshold on the golden set | Fix structured outputs before adding anything |
| End W4 | Dad approves/corrects ≥1 job unaided | H2 unsupported; simplify or abandon agent autonomy |
| End W6 | ≥1 real job recovered **and** caller reply rate above threshold | Diagnose before scaling |

## 9. Out of scope for 6 weeks

Invoicing, accounting, payments, compliance surface area, social/procurement agents,
multi-agent orchestration, polished UI, real-time voice, distributed architecture.

## 10. Reference library

Fitzpatrick (discovery) · Ries (MVP, metrics) · Thiel (beachhead, 10x) ·
Lubanovic (FastAPI) · Huyen (agents, evaluation, HITL) · Kleppmann (scale, later).

**Gap:** positioning/pricing/GTM — e.g. *Obviously Awesome*, *Traction*, *$100M Offers*.

## Open questions

- Which beachhead: carpenters nationally, or all trades in one region?
- What is the 10x axis, and can it be evidenced rather than asserted?
- Reply-rate threshold for H6 — set after the first live week, then freeze it.

## Change history

- **0.2 (2026-11-04)** — discovery and carrier test moved pre-sprint; Dad live Week 4;
  real-time voice deferred; AI barred from free-text customer SMS; H5 replaced; H6/H7 added;
  Week 3 gate made numeric.
- **0.1** — initial draft, loosely attributed, voice in Week 5, Dad live Week 6.
