---
title: Execution Plan — what to do, in order
status: draft
version: 0.3
last_updated: 2026-11-17
sources:
  - ../product/business-plan.md §6 (gates) and §7 (6-week sprint)
  - GitHub milestones: Pre-sprint gates, Week 1–6
---

# Execution Plan

One page that says what to do next. The business plan explains *why*; this page says *what*.
Each item links to its GitHub issue. Work the phases in order: a phase does not start until the
one before it has passed its gate.

Time budget: about 14 hours a week, roughly 2 hours a day ([business plan §7](../product/business-plan.md)).

## Where things stand (2026-11-17)

- **Built:** Weeks 1–5. Webhooks, auto-text, extraction, golden-set gate (passed), dashboard,
  metrics, deployment, hardening, voicemail-to-text.
- **Not live.** Go-live (#31) waits for the pre-sprint gates below, which D-010 deferred.
- **Blocking everything else:** the G0a decision (#143). Interview 1 did not support H1. Until
  #143 is decided, no new missed-call feature work. Open sub-issues: five more interviews with
  traders who mostly do private work (#140), the envelope walkthrough for H9 (#141), and asking
  Dad how he reacts to a text back (#142).

## Pre-sprint gates

| Order | Issue | Who | Task | Done when |
|---|---|---|---|---|
| 1 | [#10](https://github.com/Mario8289/agent-ant/issues/10) | You | Six Mom Test interviews using [interview script](../discovery/interview-script.md). Record in [discovery findings](../discovery/findings.md) | At least 6 interviews logged, names and numbers kept out of the repo |
| 2 | [#15](https://github.com/Mario8289/agent-ant/issues/15) | You | Choose the beachhead segment (H5) | Decision recorded in [decision records](../decisions/README.md) |
| 3 | [#12](https://github.com/Mario8289/agent-ant/issues/12) | Me, in `spikes/` | Five precursor spikes, one per learning-track row 1–5 (see below) | Each spike's "done when" test passes |
| 4 | [#47](https://github.com/Mario8289/agent-ant/issues/47) | Parked | Forwarding on Dad's real plan | Not started. Needed before any real customer call |
| 5 | [#17](https://github.com/Mario8289/agent-ant/issues/17) | You | Grant and credit applications per [grants timeline](./grants.md) | Not on the critical path; can run in parallel |

**Gate check before Week 1:**
- **G0a** (#10): at least 3 of 6 interviewees describe a specific missed call and a lost job.
- **G0b** (#47): forwarding works on Dad's real plan. Currently open. Build work waits for this, or for a logged decision to accept the risk.
- **G0c** (#12): all five spikes pass.

If G0a fails, stop and reconsider the wedge.

**Update 2026-11-07 ([D-010](../decisions/README.md)):** Week 1 starts before G0a, G0b and #15 are
done, on the founder's decision. They are deferred, not dropped. If G0a fails later, stop.

### G0c: Precursor Ready Check and the five spikes (#12)

The Ready Check:

1. FastAPI server accepts a **form-encoded** POST webhook and returns a valid response.
2. LLM returns a Pydantic-validated structured object from messy text, with a repair path.
3. Twilio number triggers the webhook on a missed call **on Dad's real carrier**.
4. Write and read a record in Supabase from Python, with a working unique constraint.
5. Build a LangGraph state graph with one conditional branch and a Postgres checkpointer.

The spikes are learning exercises in `spikes/`, kept out of `apps/`, `agents/` and `packages/`. They use
synthetic data only.

| Spike | Learning row | Done when |
|---|---|---|
| `spikes/01-form-webhook` | 1 — FastAPI, form-encoded webhooks | A local endpoint accepts a form POST and returns valid TwiML |
| `spikes/02-twilio-signature` | 2 — Twilio signature verification | A request with a valid `X-Twilio-Signature` passes and a tampered one is rejected |
| `spikes/03-idempotent-insert` | 3 — Postgres unique constraints | A duplicate `idempotency_key` is rejected and handled, not a crash |
| `spikes/04-structured-output` | 4 — Pydantic and repair loop | Messy text becomes a validated object; invalid output triggers a bounded repair |
| `spikes/05-langgraph-branch` | 5 — StateGraph, interrupt, checkpointer | A synthetic message runs extract → validate → interrupt → approve, and resumes |

All five spikes are built and merged. Item 3 depends on G0b.

## Week 1 — missed call triggers a text (product code starts here)

Started early under [D-010](../decisions/README.md), before the gates pass. Order matters: persist first, then process.

| Order | Issue | Task |
|---|---|---|
| 1 | [#19](https://github.com/Mario8289/agent-ant/issues/19) | Persist raw events with a unique `idempotency_key`; Alembic baseline |
| 2 | [#18](https://github.com/Mario8289/agent-ant/issues/18) | Missed-call webhook with `X-Twilio-Signature` verification (R5) |
| 3 | [#20](https://github.com/Mario8289/agent-ant/issues/20) | Fixed-template auto-SMS as a background task. Decide the sender identity (R2) first |
| 4 | [#21](https://github.com/Mario8289/agent-ant/issues/21) | SMS reply webhook: persist the raw reply |

**Week 1 done when:** a missed call triggers the template text, and the reply is stored.

**Done 2026-11-08**, verified end to end on a real phone rather than with fixtures: a call to the
Twilio number was stored (`CA28eb84...`), the template SMS was delivered (`SMef63a3...`), and
the reply was stored and linked to that call (`SM5f172a...`, `related_event_id` = the call row).
Deferred from this week: `HELP`/`STOP` handling (#72), persisting outbound messages (#73).

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

**End of week 6, continue only if:** at least one real job was recovered **and** the caller reply rate is above threshold ([business plan §8](../product/business-plan.md)).

## Open items that don't fit a week

- **Customer-set forwarding** (known limitation in [forwarding test runbook](../runbooks/telephony-forwarding-test.md)): the
  app can't set it. Decide the onboarding approach before Week 4.
- **Region** (US1 or IE1) and the Twilio DPA: decide before Week 4.

## Change history

- **0.3 (2026-11-17)**: "Where things stand" added; the G0c Ready Check moved here from the old
  doc 05 (D-032).
- **0.2 (2026-11-07)** — Week 1 starts before the gates (D-010); spikes marked built.
- **0.1 (2026-11-06)** — first version, consolidated from the business plan and the milestones.
