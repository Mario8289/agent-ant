---
title: Decision Records
status: draft
version: 1.0
last_updated: 2026-11-17
sources:
  - Nygard — Documenting Architecture Decisions (ADR format) — verified
  - Ries — The Lean Startup (2011) — validated learning — verified
---

# Decision Records

## Purpose

Each file records one decision: what was decided, why, and whether it can be undone. This is
the place to look for answers to questions like "why Bedrock and not the Anthropic API?" or
"why is the dashboard inside the API?"

This folder replaces the old single-file decision log (`docs/06-decision-log.md`) and the
separate `docs/adr/` folder (D-032). The IDs did not change: `D-NNN` in code, issues and PRs
still points to the same decision.

## Rules

1. **One decision per file**, named `D-NNN-short-slug.md`. Copy [template.md](./template.md).
   Take the next free number and add a row to the index below in the same PR.
2. **Append-only.** Never delete a decision or rewrite what it says. To change one, write a new
   decision and set the old one's status to `superseded by D-NNN`. Fixing a broken link or a
   typo is allowed.
3. **Every decision names a source**: a doc, a book, an interview or a measurement.
4. **Status** is one of `proposed`, `accepted` or `superseded by D-NNN`.
5. **Reversible?** gets an honest answer: `cheap`, `costly` or `one-way`.
6. **List the options you rejected** when there was a real choice. That section is the one
   people skip and the one that is most useful later.

## Index

| ID | Decision | Status | Date |
|---|---|---|---|
| [D-001](./D-001-wedge-missed-call.md) | Wedge is missed call → auto-text → job record | accepted | 2026-11-04 |
| [D-002](./D-002-defer-real-time-voice.md) | Real-time voice deferred past Week 6 | accepted | 2026-11-04 |
| [D-003](./D-003-one-agent-prototype.md) | 6-week goal is a one-agent prototype | accepted | 2026-11-04 |
| [D-004](./D-004-fixed-template-sms.md) | Customer-facing SMS is a fixed template only | accepted | 2026-11-04 |
| [D-005](./D-005-one-service-one-postgres.md) | One service, one Postgres, no broker | accepted | 2026-11-04 |
| [D-006](./D-006-dad-live-week-4.md) | Dad goes live in Week 4 | accepted | 2026-11-04 |
| [D-007](./D-007-uv-monorepo-layout.md) | Python-first `uv` workspace monorepo, `agent_ant_*` naming | accepted | 2026-11-04 |
| [D-008](./D-008-langgraph-orchestration.md) | Orchestration: LangGraph for the missed-call agent | accepted | 2026-11-05 |
| [D-009](./D-009-swappable-llm-provider.md) | LLM provider: swappable for the MVP, DPA-backed lock before live | accepted | 2026-11-05 |
| [D-010](./D-010-build-before-gates.md) | Start Week 1 build before G0a, G0b and the beachhead decision | accepted | 2026-11-07 |
| [D-011](./D-011-sms-sender-twilio-number.md) | Auto-SMS sender: Twilio number plus business name in the text (R2) | accepted | 2026-11-07 |
| [D-012](./D-012-audit-trail-tables.md) | Audit trail: two tables (`llm_output_audits` + `human_edits`), `job_id` deferred | accepted | 2026-11-09 |
| [D-013](./D-013-job-records-background-extraction.md) | `job_records` table + background extraction; the approval interrupt stays Week 4 | accepted | 2026-11-09 |
| [D-014](./D-014-dashboard-in-api.md) | Dashboard lives in the API (one service), server-rendered | accepted | 2026-11-09 |
| [D-015](./D-015-eu-cross-region-inference.md) | LLM inference: `eu.*` cross-region acceptable, `global.*` rejected | accepted | 2026-11-10 |
| [D-016](./D-016-extraction-model-sonnet-4-6.md) | Extraction model: Claude Sonnet 4.6 for now (newer models account-gated) | accepted | 2026-11-10 |
| [D-017](./D-017-h8-accuracy-gate.md) | H8 accuracy gate: containment metric for `job_type`, held-out `golden_v2`, frozen pass line (H8a) | accepted | 2026-11-13 |
| [D-018](./D-018-bedrock-provider-lock.md) | LLM provider locked: AWS Bedrock, `eu.anthropic.claude-sonnet-4-6` (R4) | accepted | 2026-11-13 |
| [D-019](./D-019-help-stop-opt-out.md) | HELP/STOP opt-out: handle ourselves, confirm STOP and reply HELP (fixed templates) | accepted | 2026-11-13 |
| [D-020](./D-020-app-runner-hosting.md) | Production hosting: AWS App Runner (containers) for the stateless API (#29) | accepted | 2026-11-13 |
| [D-021](./D-021-outbound-sms-persisted.md) | Outbound SMS is persisted (`outbound_messages`) with status callbacks and 30-day retention (#73) | accepted | 2026-11-13 |
| [D-022](./D-022-business-metrics.md) | Business metrics frozen: capture rate, reply rate, jobs booked, edit rate (#30) | accepted | 2026-11-13 |
| [D-023](./D-023-sms-retry-policy.md) | Retry policy: failed SMS sends retried up to 3 attempts, then dead-lettered (#34) | accepted | 2026-11-13 |
| [D-024](./D-024-extraction-retry-policy.md) | Retry policy: failed extractions retried up to 3 attempts, then dead-lettered (#34) | accepted | 2026-11-13 |
| [D-025](./D-025-outbound-retention-purge.md) | Retention purge: outbound personal fields redacted at 30 days; wider retention deferred (#34) | accepted | 2026-11-13 |
| [D-026](./D-026-slack-support-alerts.md) | Support alerting via Slack incoming webhook (operator, not customer) (#94) | accepted | 2026-11-13 |
| [D-027](./D-027-retention-and-erasure.md) | Retention + erasure: raw/audit data redacted at 90 days, job records kept, on-request erase (#95) | accepted | 2026-11-13 |
| [D-028](./D-028-cdk-scheduled-jobs.md) | Schedule retry/purge via CDK: EventBridge Scheduler → ECS Fargate (#96) | accepted | 2026-11-13 |
| [D-029](./D-029-voicemail-to-text.md) | Voicemail-to-text: async Twilio transcription feeds the extraction pipeline (#33) | accepted | 2026-11-14 |
| D-030 | *Reserved* for the customer and job lifecycle decision (#122). Not yet written. | — | — |
| [D-031](./D-031-agent-roadmap-planned.md) | Agent roadmap is planned, not built: epics for agents 1–4 blocked by the prototype and its gates | accepted | 2026-11-14 |
| [D-032](./D-032-documentation-structure.md) | Documentation structure: PRD, design doc, one file per decision, C4 diagrams | accepted | 2026-11-17 |

## Anti-patterns

- ⚠️ **Editing history.** Rewriting a decision hides why the choice was made. Supersede it.
- ⚠️ **Decisions with no source.** A decision that cannot cite a doc, interview or measurement
  is an opinion. Mark it `proposed`.
- ⚠️ **Recording only the choice.** Without context and consequences, nobody can re-evaluate
  the decision when conditions change.

## Open questions

- Which beachhead segment: carpenters nationally, or one region? See issue #15. D-010 deferred
  it. Until it is decided, the working assumption is tradespeople in general.

## Change history

- **1.0 (2026-11-17)**: split from `06-decision-log.md` into one file per decision (D-032).
  ADR 0001 merged into D-008 and ADR 0002 into D-009. History before the split is in the old
  log's change history and in `git log --follow`.
