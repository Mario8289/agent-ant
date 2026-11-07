---
title: Execution Plan — what to do, in order
status: draft
version: 0.2
last_updated: 2026-11-07
sources:
  - 00-business-plan.md §6 (gates) and §7 (6-week sprint)
  - GitHub milestones: Pre-sprint gates, Week 1–6
---

# 09 — Execution Plan

One page that says what to do next. The business plan explains *why*; this page says *what*.
Each item links to its GitHub issue. Work the phases in order: a phase does not start until the
one before it has passed its gate.

Time budget: about 14 hours a week, roughly 2 hours a day ([00 §7](./00-business-plan.md)).

## Right now: pre-sprint gates

| Order | Issue | Who | Task | Done when |
|---|---|---|---|---|
| 1 | [#10](https://github.com/Mario8289/agent-ant/issues/10) | You | Six Mom Test interviews using [02](./02-mom-test-script-dad.md). Record in [03](./03-requirements-capture-sheet.md) | At least 6 interviews logged, names and numbers kept out of the repo |
| 2 | [#15](https://github.com/Mario8289/agent-ant/issues/15) | You | Choose the beachhead segment (H5) | Decision recorded in [06](./06-decision-log.md) |
| 3 | [#12](https://github.com/Mario8289/agent-ant/issues/12) | Me, in `spikes/` | Five precursor spikes, one per learning-track row 1–5 (see below) | Each spike's "done when" test passes |
| 4 | [#47](https://github.com/Mario8289/agent-ant/issues/47) | Parked | Forwarding on Dad's real plan | Not started. Needed before any real customer call |
| 5 | [#17](https://github.com/Mario8289/agent-ant/issues/17) | You | Grant and credit applications per [04](./04-grants-timeline.md) | Not on the critical path; can run in parallel |

**Gate check before Week 1:**
- **G0a** (#10): at least 3 of 6 interviewees describe a specific missed call and a lost job.
- **G0b** (#47): forwarding works on Dad's real plan. Currently open. Build work waits for this, or for a logged decision to accept the risk.
- **G0c** (#12): all five spikes pass.

If G0a fails, stop and reconsider the wedge.

**Update 2026-11-07 ([D-010](./06-decision-log.md)):** Week 1 starts before G0a, G0b and #15 are
done, on the founder's decision. They are deferred, not dropped. If G0a fails later, stop.

### The five spikes (#12)

These are learning exercises in `spikes/`, kept out of `apps/`, `agents/` and `packages/`. They use
synthetic data only.

| Spike | Learning row | Done when |
|---|---|---|
| `spikes/01-form-webhook` | 1 — FastAPI, form-encoded webhooks | A local endpoint accepts a form POST and returns valid TwiML |
| `spikes/02-twilio-signature` | 2 — Twilio signature verification | A request with a valid `X-Twilio-Signature` passes and a tampered one is rejected |
| `spikes/03-idempotent-insert` | 3 — Postgres unique constraints | A duplicate `idempotency_key` is rejected and handled, not a crash |
| `spikes/04-structured-output` | 4 — Pydantic and repair loop | Messy text becomes a validated object; invalid output triggers a bounded repair |
| `spikes/05-langgraph-branch` | 5 — StateGraph, interrupt, checkpointer | A synthetic message runs extract → validate → interrupt → approve, and resumes |

All five spikes are built (PR #65 for spike 5 pending merge).

## Week 1 — missed call triggers a text (product code starts here)

Started early under [D-010](./06-decision-log.md), before the gates pass. Order matters: persist first, then process.

| Order | Issue | Task |
|---|---|---|
| 1 | [#19](https://github.com/Mario8289/agent-ant/issues/19) | Persist raw events with a unique `idempotency_key`; Alembic baseline |
| 2 | [#18](https://github.com/Mario8289/agent-ant/issues/18) | Missed-call webhook with `X-Twilio-Signature` verification (R5) |
| 3 | [#20](https://github.com/Mario8289/agent-ant/issues/20) | Fixed-template auto-SMS as a background task. Decide the sender identity (R2) first |
| 4 | [#21](https://github.com/Mario8289/agent-ant/issues/21) | SMS reply webhook: persist the raw reply |

**Week 1 done when:** a missed call triggers the template text, and the reply is stored.

## Week 2 — messy text becomes a job record

| Order | Issue | Task |
|---|---|---|
| 1 | [#22](https://github.com/Mario8289/agent-ant/issues/22) | LLM client: structured output, Pydantic validation, repair path |
| 2 | [#23](https://github.com/Mario8289/agent-ant/issues/23) | `missed_call` extraction agent with versioned prompt v1 (LangGraph per D-008) |
| 3 | [#24](https://github.com/Mario8289/agent-ant/issues/24) | Audit tables: `LLMOutputAudit` and `human_edits` (R6) |

**Week 2 done when:** a synthetic reply becomes a validated record, with an audit row.

## Week 3 — measure accuracy

| Order | Issue | Task |
|---|---|---|
| 1 | [#25](https://github.com/Mario8289/agent-ant/issues/25) | Golden set of labelled synthetic messages |
| 2 | [#26](https://github.com/Mario8289/agent-ant/issues/26) | Eval harness and a frozen accuracy threshold (H8) |
| 3 | [#27](https://github.com/Mario8289/agent-ant/issues/27) | **Gate:** accuracy review. Below threshold, fix extraction before adding anything |

## Week 4 — Dad goes live (text only)

| Order | Issue | Task |
|---|---|---|
| 1 | [#16](https://github.com/Mario8289/agent-ant/issues/16) | Lock one DPA-backed LLM provider. Also settle the Twilio DPA and region (US1 or IE1). **Before any real data** |
| 2 | [#29](https://github.com/Mario8289/agent-ant/issues/29) | Deployment: hosting, secrets, production DPA check |
| 3 | [#28](https://github.com/Mario8289/agent-ant/issues/28) | Minimal dashboard: approve, edit, reject |
| 4 | [#30](https://github.com/Mario8289/agent-ant/issues/30) | Metrics: capture rate, reply rate, jobs booked, edit rate |
| 5 | [#31](https://github.com/Mario8289/agent-ant/issues/31) | Dad goes live, text only |
| 6 | [#32](https://github.com/Mario8289/agent-ant/issues/32) | **Gate:** Dad approves or corrects at least one real job unaided (H2) |

Nothing reaches a real customer before #16 is closed.

## Week 5 — harden or add voicemail

| Order | Issue | Task |
|---|---|---|
| 1 | [#34](https://github.com/Mario8289/agent-ant/issues/34) | Retries, failure flagging, alerting, data retention basics |
| 2 | [#33](https://github.com/Mario8289/agent-ant/issues/33) | Optional: async voicemail-to-text. Skip it if hardening runs late |

## Week 6 — measure and decide

| Order | Issue | Task |
|---|---|---|
| 1 | [#35](https://github.com/Mario8289/agent-ant/issues/35) | Live measurement and write-up (H6, H8) |
| 2 | [#36](https://github.com/Mario8289/agent-ant/issues/36) | Pricing conversation, deposit ask (H3), referral ask (H7) |
| 3 | [#37](https://github.com/Mario8289/agent-ant/issues/37) | **Gate:** continue or kill, and the week 7 plan |

**End of week 6, continue only if:** at least one real job was recovered **and** the caller reply rate is above threshold ([00 §8](./00-business-plan.md)).

## Open items that don't fit a week

- **Customer-set forwarding** (known limitation in [08](./08-telephony-forwarding-test.md)): the
  app can't set it. Decide the onboarding approach before Week 4.
- **Region** (US1 or IE1) and the Twilio DPA: decide before Week 4.

## Change history

- **0.2 (2026-11-07)** — Week 1 starts before the gates (D-010); spikes marked built.
- **0.1 (2026-11-06)** — first version, consolidated from the business plan and the milestones.
