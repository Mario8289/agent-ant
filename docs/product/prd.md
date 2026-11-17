---
title: PRD — Missed-call → booked-job assistant
status: draft
version: 1.0
last_updated: 2026-11-17
sources:
  - business-plan.md §1, §5, §6, §8, §9
  - ../discovery/hypotheses.md
  - D-004, D-022, D-017, D-029
---

# PRD — Missed-call → booked-job assistant

What we are building and why, on one page. How it is built is in the
[design doc](../design/design-doc.md). The wider business case (competitors, the 6-week sprint)
is in the [business plan](./business-plan.md).

> **Status (2026-11-17).** The MVP is built (Weeks 1–5) but **not live**. The pre-sprint gates
> were deferred under D-010 and now block go-live. The first discovery interview did not support
> H1, so the G0a decision (#143) may change the wedge. No new missed-call features are built
> until that decision is made.

## Problem

A sole trader is on a ladder, under a sink or driving when the phone rings. The call goes
unanswered, the caller rings the next trader on the list, and the job is lost. The trader has
no time to call everyone back, and doesn't know which missed calls were real work.

This is an **assumption, not a finding** (H1). Interview 1 did not support it: the trader
misses calls daily but could not name a lost job. See [findings](../discovery/findings.md).

## Users

| User | Who | What they need |
|---|---|---|
| **Trader** (primary) | A UK sole trader such as a carpenter or plumber. Working assumption until #15: tradespeople in general (D-010). Design partner: Dad, a carpenter | Missed callers captured as jobs they can act on, without typing anything |
| **Caller** | A member of the public who rang the trader and got no answer | To be acknowledged quickly and know how to give job details |
| **Operator** | The founder | To know when something fails, without reading logs |

## Goals and success metrics

| Goal | Metric (frozen in D-022) | Pass line | Hypothesis |
|---|---|---|---|
| Callers engage with the text | `reply_rate` = replies ÷ auto-texts sent | Set after the first live week, then frozen | H6 |
| Missed calls become jobs | `capture_rate` = job records ÷ missed calls | Reported, no line | — |
| Jobs actually get booked | `jobs_booked` = approved job records | ≥1 real job recovered by end of Week 6 | — |
| Extraction is good enough | `edit_rate` = jobs with a correction ÷ job records; golden-set accuracy | `job_type` ≥ 0.80, `urgency` ≥ 0.90 on held-out set (passed, D-017); live edit rate decides | H8a |
| Trader trusts it | Trader approves or corrects a real job unaided | ≥1 by end of Week 4 | H2 |
| Trader would pay | Deposit or pre-order | ≥1 | H3 |

The vanity metric we do not report as progress: total calls logged.

## User stories

1. **Auto-text.** As a caller whose call went unanswered, I get a text that names the
   business and asks for my name, the job and where it is, so I know the trader
   will see my enquiry.
2. **Reply captured.** As a trader, when a caller replies, I see a job record with name, job
   type, location, urgency and preferred date filled in, so I don't have to read and retype
   the text.
3. **Voicemail captured.** As a trader, if a caller leaves a voicemail instead of texting, it
   becomes a job record in the same way (D-029).
4. **Approve, edit, reject.** As a trader, I can approve a job, correct any field, or reject
   it (for example a duplicate) from a browser. Nothing counts as booked until I approve it.
5. **Opt out.** As a caller, I can reply STOP to stop texts and HELP to get the instructions
   again (D-019). The trader still sees that I called.
6. **Failures surface.** As the operator, I get a Slack alert when a text fails to send or an
   extraction is dead-lettered, and the dashboard lists them (D-023, D-024, D-026).
7. **Forgotten on request.** As a caller, I can ask for my details to be erased (D-027).

## Scope

**In scope (MVP):**

- Carrier forwards unanswered calls to a Twilio number. Customer-facing SMS is a fixed
  template only.
- LLM extraction of the reply or voicemail transcript into a validated job record.
- Server-rendered dashboard for the trader to approve, edit or reject, with metrics.
- Retries, dead-lettering, operator alerts, data retention and erasure.

**Out of scope (MVP):** real-time voice, invoicing, accounting, payments, quoting, a second
agent, multi-agent orchestration, social or procurement agents, a polished UI, distributed
architecture. What might follow the MVP is in the [roadmap](./roadmap.md). It is planned but
not built (D-031).

## Non-negotiables

These limit what the product may do. They are not engineering preferences.

- **The AI never writes to customers.** Every message a caller receives is a fixed template.
  What the AI produces goes only to the trader (D-004).
- **A human approves every job.** Nothing is confirmed without the trader.
- **No real customer data before go-live.** Development uses synthetic data only. Live data
  is processed only under a DPA with no training on it (D-018).
- **No lead is silently lost.** A missed call is stored even if the text fails or the caller
  opted out (D-019).

## Gates

| Gate | Test | Pass line | State |
|---|---|---|---|
| **G0a** discovery | 6 interviews | ≥3 of 6 recall a specific missed call **and** lost job (H1) | 0 of 1. Decision in #143 |
| **G0b** forwarding | Forward the trader's real phone to Twilio, caller ID kept | Works on the real plan | Passed on a test phone, not on Dad's plan (#47) |
| **G0c** skills | Five precursor spikes | All pass | All five spikes built and merged; #12 not yet closed |
| **End W3** | Golden-set accuracy | H8a line | passed (smoke test) |
| **End W4** | Trader approves or corrects a real job unaided (H2) | ≥1 | not started |
| **End W6** | Real job recovered **and** reply rate above line | both | not started |

If G0a fails, stop and reconsider the wedge (business plan §6).

## Open questions

| Question | Owner | Where |
|---|---|---|
| Does the missed-call wedge survive discovery, or is receipts/paperwork the better wedge (H9)? | Founder | #143 |
| Which beachhead segment: one trade, one region? | Founder | #15 |
| How does a trader set up call forwarding without help? | Founder | [Forwarding runbook](../runbooks/telephony-forwarding-test.md) |
| What reply rate counts as a pass for H6? | Founder, after the first live week | D-022 |

## Change history

- **1.0 (2026-11-17)**: Created (D-032). Brings together the business plan (§1, §5, §6, §8,
  §9), the hypothesis table, D-022 and the agent roadmap. No new decisions.
