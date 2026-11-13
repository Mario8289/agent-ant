---
title: Decision Log
status: draft
version: 0.21
last_updated: 2026-11-13
sources:
  - Nygard — Documenting Architecture Decisions (ADR format) — verified
  - Ries — The Lean Startup (2011) — validated learning — verified
---

# 06 — Decision Log

## Purpose

One place to see what was decided, why, and whether it can be undone. Short decisions live
here as a single entry. Decisions that need more space get a full ADR in
[adr/](./adr/README.md) and are linked from the entry.

## Rules

1. **Append-only.** Never delete or rewrite an entry. To change a decision, add a new entry
   and mark the old one `superseded by D-NNN`.
2. **Every entry names a source** — a doc, a book, an interview, or a measurement.
3. **Status** is one of `proposed`, `accepted`, `superseded`.
4. **Reversible?** is answered honestly: `cheap`, `costly`, or `one-way`.

## Entry template

```markdown
### D-NNN — Title
- **Date:** YYYY-MM-DD
- **Status:** proposed | accepted | superseded by D-NNN
- **Context:** what forced the decision
- **Decision:** what was chosen
- **Consequences:** what this makes easier and harder
- **Source:** doc, book, interview or data
- **Reversible?:** cheap | costly | one-way
```

## Index

| ID | Decision | Status | Date |
|---|---|---|---|
| D-001 | Wedge is missed call → auto-text → job record | accepted | 2026-11-04 |
| D-002 | Real-time voice deferred past Week 6 | accepted | 2026-11-04 |
| D-003 | 6-week goal is a one-agent prototype | accepted | 2026-11-04 |
| D-004 | Customer-facing SMS is a fixed template only | accepted | 2026-11-04 |
| D-005 | One service, one Postgres, no broker | accepted | 2026-11-04 |
| D-006 | Dad goes live in Week 4 | accepted | 2026-11-04 |
| D-007 | Python-first `uv` workspace monorepo, `agent_ant_*` naming | accepted | 2026-11-04 |
| D-008 | Orchestration: LangGraph for the missed-call agent | accepted | 2026-11-05 |
| D-009 | LLM provider: swappable for the MVP, DPA-backed lock before live | accepted | 2026-11-05 |
| D-010 | Start Week 1 build before G0a, G0b and the beachhead decision | accepted | 2026-11-07 |
| D-011 | Auto-SMS sender: Twilio number plus business name in the text (R2) | accepted | 2026-11-07 |
| D-012 | Audit trail: two tables (`llm_output_audits` + `human_edits`), `job_id` deferred | accepted | 2026-11-09 |
| D-013 | `job_records` table + background extraction; the approval interrupt stays Week 4 | accepted | 2026-11-09 |
| D-014 | Dashboard lives in the API (one service), server-rendered | accepted | 2026-11-09 |
| D-015 | LLM inference: `eu.*` cross-region acceptable, `global.*` rejected | accepted | 2026-11-10 |
| D-016 | Extraction model: Claude Sonnet 4.6 for now (newer models account-gated) | accepted | 2026-11-10 |
| D-017 | H8 accuracy gate: containment metric for `job_type`, held-out `golden_v2`, frozen pass line (H8a) | accepted | 2026-11-13 |
| D-018 | LLM provider locked: AWS Bedrock, `eu.anthropic.claude-sonnet-4-6` (R4) | accepted | 2026-11-13 |
| D-019 | HELP/STOP opt-out: handle ourselves, confirm STOP and reply HELP (fixed templates) | accepted | 2026-11-13 |
| D-020 | Production hosting: AWS App Runner (containers) for the stateless API (#29) | accepted | 2026-11-13 |
| D-021 | Outbound SMS is persisted (`outbound_messages`) with status callbacks and 30-day retention (#73) | accepted | 2026-11-13 |
| D-022 | Business metrics frozen: capture rate, reply rate, jobs booked, edit rate (#30) | accepted | 2026-11-13 |
| D-023 | Retry policy: failed SMS sends retried up to 3 attempts, then dead-lettered (#34) | accepted | 2026-11-13 |
| D-024 | Retry policy: failed extractions retried up to 3 attempts, then dead-lettered (#34) | accepted | 2026-11-13 |
| D-025 | Retention purge: outbound personal fields redacted at 30 days; wider retention deferred (#34) | accepted | 2026-11-13 |
| D-026 | Support alerting via Slack incoming webhook (operator, not customer) (#94) | accepted | 2026-11-13 |
| D-027 | Retention + erasure: raw/audit data redacted at 90 days, job records kept, on-request erase (#95) | accepted | 2026-11-13 |
| D-028 | Schedule retry/purge via CDK: EventBridge Scheduler → ECS Fargate (#96) | accepted | 2026-11-13 |

## Entries

### D-001 — Wedge is missed call → auto-text → job record
- **Date:** 2026-11-04
- **Status:** accepted
- **Context:** A vertical assistant for sole traders could start anywhere (invoicing, quoting,
  scheduling). The first product must be demoable quickly and avoid financial compliance.
- **Decision:** Start with the missed call. It is a live, frequent, monetisable loss.
  Invoice-chasing is deferred until the wedge has earned trust.
- **Consequences:** Everything depends on carrier forwarding (R1) and on callers replying to
  an SMS (H6). Both are tested before and early in the build.
- **Source:** [00-business-plan.md](./00-business-plan.md) §1
- **Reversible?:** cheap — no code exists yet.

### D-002 — Real-time voice deferred past Week 6
- **Date:** 2026-11-04
- **Status:** accepted
- **Context:** v0.1 put voice in Week 5. It was the highest-risk component (latency, cost,
  complexity) and no hypothesis requires it.
- **Decision:** Real-time voice is out of scope. Optional async voicemail-to-text may appear
  in Week 5.
- **Consequences:** The MVP is text-only. Coverage is lower for callers who leave no voicemail.
- **Source:** [00-business-plan.md](./00-business-plan.md) §7, [05-architecture-and-schema.md](./05-architecture-and-schema.md)
- **Reversible?:** cheap

### D-003 — 6-week goal is a one-agent prototype
- **Date:** 2026-11-04
- **Status:** accepted
- **Context:** The repo is structured for several agents and products, but only one
  assumption set has been defined.
- **Decision:** Build one agent (`missed_call`). Multi-agent orchestration, social and
  procurement agents are out of scope for 6 weeks. The repo layout may have room for more,
  but no second agent is built.
- **Consequences:** Shared code in `packages/core` is extracted only when a second consumer
  exists, or when the first agent clearly needs it.
- **Source:** [00-business-plan.md](./00-business-plan.md) §9
- **Reversible?:** cheap

### D-004 — Customer-facing SMS is a fixed template only
- **Date:** 2026-11-04
- **Status:** accepted
- **Context:** An LLM writing to customers carries reputational risk while H2 and H6 are
  unproven.
- **Decision:** The AI never writes free text to customers. LLM output goes to Dad only.
- **Consequences:** Replies are less personal. Hallucination blast radius is capped.
- **Source:** Huyen — AI Engineering (2025); [00-business-plan.md](./00-business-plan.md) §5
- **Reversible?:** cheap, but revisit only with evidence from live data.

### D-005 — One service, one Postgres, no broker
- **Date:** 2026-11-04
- **Status:** accepted
- **Context:** A solo founder at ~2 hrs/day cannot operate distributed infrastructure.
- **Decision:** One FastAPI service, one Postgres (Supabase), FastAPI background tasks. No
  Kafka, no queue broker, no microservices.
- **Consequences:** Durability relies on persisting the raw event first. A crash mid-task is
  recovered by reprocessing stored events.
- **Source:** Kleppmann & Riccomini — DDIA, 2nd ed. (2026); [05-architecture-and-schema.md](./05-architecture-and-schema.md)
- **Reversible?:** costly once real traffic and data exist.

### D-006 — Dad goes live in Week 4
- **Date:** 2026-11-04
- **Status:** accepted
- **Context:** v0.1 had Dad live in Week 6, giving one week of real data.
- **Decision:** Go live text-only in Week 4, for three weeks of real data.
- **Consequences:** Hardening is compressed; the Week 4 gate carries more weight.
- **Source:** Ries — The Lean Startup (2011), shorten the loop; [00-business-plan.md](./00-business-plan.md) §7
- **Reversible?:** cheap

### D-007 — Python-first `uv` workspace monorepo, `agent_ant_*` naming
- **Date:** 2026-11-04
- **Status:** accepted
- **Context:** The repo must hold multiple agents and products without becoming a tangle.
- **Decision:**
  - `uv` workspace with `apps/` (deployables), `agents/` (one package per agent) and
    `packages/` (shared libraries). Dependencies point one way: apps → agents → core.
  - Python packages are named `agent_ant_*`.
  - Tooling: `ruff`, `pyright`, `pytest`, `just`, Alembic.
  - `apps/dashboard` is a placeholder until Week 4.
  - Prompts are versioned files; evals live in `evals/`, separate from unit tests.
- **Consequences:** Slightly more files up front than a single package; cheaper to add a
  second agent or product later.
- **Source:** Planning discussion 2026-11-04; tracked in the Foundation milestone.
- **Reversible?:** costly once many packages exist; cheap now.

### D-008 — Orchestration: LangGraph for the missed-call agent
- **Date:** 2026-11-05
- **Status:** accepted
- **Context:** The flow has three branch points (valid vs. invalid extraction, repair
  exhausted, human approve/edit/reject) and is expected to become multi-turn. The first draft
  recommended plain Python steps; the founder rejected that so the orchestration model is in
  place before the flow grows.
- **Decision:** LangGraph `StateGraph` from Week 2, with a Postgres checkpointer and
  `interrupt()` for human approval. The dependency lives in `agents/missed_call` only;
  `packages/core` stays framework-free. Nodes call plain functions, so business logic stays
  unit-testable.
- **Consequences:** A framework to learn, pin and debug; checkpoint tables need a migration;
  graph wiring needs its own test harness. In exchange, branching, resumability and
  human-in-the-loop come from the framework. G0c item 5 is active again and the LangGraph
  learning row moves up.
- **Source:** [adr/0001-orchestration-langgraph.md](./adr/0001-orchestration-langgraph.md)
- **Reversible?:** costly once the graph and checkpoints are in production; cheap now.

### D-009 — LLM provider: swappable for the MVP, DPA-backed lock before live
- **Date:** 2026-11-05
- **Status:** accepted
- **Context:** Customer messages are personal data under UK GDPR, so live traffic needs a DPA,
  a UK transfer mechanism and a no-training commitment. There is no live traffic yet, and the
  founder does not want prompts and evals tuned to one model before the MVP is proven.
- **Decision:** Keep the provider swappable during the MVP and use whatever is cheapest for
  synthetic data. **Bedrock is the default** when credentials allow: AWS DPA, no training on
  inputs or outputs, and `eu-west-2` (London) for UK in-region inference. Lock one DPA-backed
  provider and re-run the golden set before Dad goes live in Week 4 (#29).
- **Chosen 2026-11-07:** Bedrock, `eu-west-2`, single-region inference, for Week 2 development.
  The model is picked when #22 starts, after checking it is offered in London.
  > **Superseded in part by D-015 (2026-11-10):** the `eu-west-2` single-region constraint is
  > relaxed to EU geography (`eu.*` profiles). The swappable-provider and DPA-lock parts stand.
- **Consequences:** R4 stays open until Week 4 — the risk being carried. Mitigations are the
  synthetic-data rule and the explicit gate. An adapter seam keeps a switch to a config change.
  Real customer messages arriving early must not be sent to the LLM.
- **Source:** [adr/0002-llm-provider.md](./adr/0002-llm-provider.md)
- **Reversible?:** cheap by design — that is the point of the decision.

### D-010 — Start Week 1 build before G0a, G0b and the beachhead decision
- **Date:** 2026-11-07
- **Status:** accepted
- **Context:** The plan says build work waits for the pre-sprint gates: G0a (6 Mom Test
  interviews, #10), G0b (forwarding on Dad's real plan, #47) and the beachhead decision (#15).
  None are done. G0c's spikes are built (#59, #60, #61, PR #65 pending merge). The founder wants to start coding and
  will do the interviews and the questionnaire later.
- **Decision:** Start Week 1 (#19, #18, #20, #21) now. Until #15 is decided, the working
  assumption is **tradespeople in general** (carpenters, plumbers and similar), not one trade.
  The gates are deferred, not dropped.
- **Consequences:** Week 1 is persist-raw-event, signature-verified webhook, fixed-template SMS
  and reply storage. None of it depends on the segment, so little is lost if the segment
  changes. The risk carried: if G0a fails or G0b fails, Week 1 effort is wasted and the
  telephony design may have to change. Deferral does not lift the other rules: no real customer
  data before #16, nothing reaches a real customer before the Week 4 gates, and a failed G0a
  still means stop and reconsider the wedge (00 §6).
- **Source:** founder decision, 2026-11-07; [00-business-plan.md](./00-business-plan.md) §6
- **Reversible?:** cheap — about one week of segment-agnostic plumbing.

### D-011 — Auto-SMS sender: Twilio number plus business name in the text (R2)
- **Date:** 2026-11-07
- **Status:** accepted
- **Context:** The auto-text (#20) must come from some sender. The caller phoned Dad's mobile,
  the unanswered call was forwarded to a Twilio number, and the text comes from that Twilio
  number, so it is a number the caller does not know. R2 (callers ignore or distrust an SMS from
  an unknown number) is open, and the founder worried it looks like a scam or invites replies to
  the wrong number.
- **Decision:** Send from the Twilio number and name the business in the fixed template ("Hi,
  it's <business>. ... This is our text line: reply with ..."). The sender is configuration,
  not code. Revisit only if the caller reply rate (H6) comes in below threshold.
- **Consequences:** Replies reach the Twilio number, so the reply webhook (#21) works. Options
  not taken, per Twilio's own pages (checked 2026-11-07): an alphanumeric sender ID (business
  name as sender) is described as one-way, so the caller could not reply and the flow breaks;
  porting Dad's mobile number into Twilio would show a number the caller knows, but UK mobile
  porting is a manual "custom" process and would redesign the carrier-forwarding approach
  (G0b). A Twilio UK mobile (+447) number is a cheaper middle option, not yet checked for cost
  or regulatory paperwork. A caller who rings the Twilio number back hears the fixed message
  and gets no human.
- **Source:** founder decision, 2026-11-07; [05-architecture-and-schema.md](./05-architecture-and-schema.md) R2;
  Twilio alphanumeric sender ID and UK porting guidelines
- **Reversible?:** cheap — the sender is a setting and the wording is one template.

### D-012 — Audit trail: two tables, `job_id` deferred
- **Date:** 2026-11-09
- **Status:** accepted
- **Context:** R6 (silent LLM drift) needs every extraction and correction logged (#24).
  The schema sketch in doc 05 shows a single `LLMOutputAudit` model with `human_edited` and
  `edit_diff` inline, and a `job_id` — but the `job_records` table it points at does not exist
  yet (that is #23).
- **Decision:** Two tables. `llm_output_audits` is an immutable snapshot keyed to
  `raw_events.id` (which exists today) with a nullable `job_id` whose foreign key is added in
  #23. `human_edits` holds one row per correction, linked to `llm_output_audits.id`, with the
  diff as JSONB (`field -> {"before", "after"}`). `human_edited` is derived from a
  `human_edits` row existing, not stored. `edit_diff` is JSONB, not a string, so the edit rate
  is queryable.
- **Consequences:** The audit is testable and useful now, before any job table exists.
  Diverges from the single-model sketch in doc 05 (updated in place). `job_id` gains a foreign
  key in a later migration, after #23 creates `job_records`.
- **Source:** [05-architecture-and-schema.md](./05-architecture-and-schema.md) R6; issue #24
- **Reversible?:** cheap — tables are new and empty.

### D-013 — `job_records` table + background extraction; the approval interrupt stays Week 4
- **Date:** 2026-11-09
- **Status:** accepted
- **Context:** With #22/#23/#24 merged, the pieces existed separately but nothing joined them:
  there was no `job_records` table, the graph was not connected to the webhook, and no audit row
  was ever written. Week 2's "done when" (a reply becomes a validated record *with an audit row*)
  was therefore still unmet.
- **Decision:** Add a `job_records` table mirroring the `JobRecord` contract, with a unique
  `idempotency_key` (the reply's `MessageSid`) and a `raw_event_id` foreign key. The SMS-reply
  webhook schedules a background task (`extract_reply`) that runs `process_reply`: extract, then
  persist a `captured` job plus an audit row (or the audit row alone on failure). The
  `llm_output_audits.job_id` foreign key deferred in D-012 is now added. The LangGraph
  `interrupt()` approval path is deliberately not wired: that is the Week 4 dashboard, so a valid
  extraction is stored `captured` and waits.
- **Consequences:** A synthetic reply now becomes a captured job plus an audit row end to end.
  The Bedrock adapter is still absent (`get_llm` returns None), so extraction is skipped until
  credentials exist (`docs/10`). `build_agent` in `graph.py` remains for the Week 4 approval path.
- **Source:** [05-architecture-and-schema.md](./05-architecture-and-schema.md) §Schema;
  [09-execution-plan.md](./09-execution-plan.md) Week 2 "done when"; D-008, D-012
- **Reversible?:** cheap — tables are new; the background-task wiring is a small seam.

### D-014 — Dashboard lives in the API (one service), server-rendered
- **Date:** 2026-11-09
- **Status:** accepted
- **Context:** #28 asks where the HITL dashboard lives relative to the `apps/dashboard`
  placeholder. D-005 commits to one service and one Postgres, so a second deployable would break
  that.
- **Decision:** The dashboard is routes plus Jinja2 templates inside `apps/api` — no second
  service. It is server-rendered to keep the repository Python-only. The approval logic
  (`approve` / `edit` / `reject`, and the `human_edits` diff) lives in `packages/core`
  (`db/approval.py`); the app layer does only HTTP and templating. `apps/dashboard` stays as a
  pointer, not a service.
- **Consequences:** One process serves both webhooks and the dashboard. A JSON API can be added
  later without moving the approval logic. No SPA or build toolchain.
- **Source:** D-005; issue #28
- **Reversible?:** cheap — the routes and templates can move to a separate app later.

### D-015 — LLM inference: `eu.*` cross-region acceptable, `global.*` rejected
- **Date:** 2026-11-10
- **Status:** accepted
- **Context:** London (`eu-west-2`) offers only a couple of Claude models in-region, so the
  founder wanted a wider choice. Spike 06 found no regulatory blocker: the EU renewed the UK's
  adequacy decisions on 19 Dec 2025 (valid to 2031), the UK treats the EEA as adequate, and
  Bedrock's `eu.*` cross-region profile stays inside EU geography.
- **Decision:** Relax D-009's single-region constraint. The `eu.*` cross-region inference profile
  is accepted, because prompts and outputs stay within EU geography. `global.*` stays rejected —
  it can route to the US (or any region) with no residency guarantee. `AWS_REGION` stays
  `eu-west-2`; `LLM_MODEL` may be an `eu.*` profile id.
- **Consequences:** More models and burst capacity than in-region London. A request may be served
  by any EU region in the profile, so data is not pinned to the UK — lawful under UK adequacy,
  but not "UK-only". The region SCP and IAM policy must keep allowing the EU regions the profile
  routes to and keep blocking `global.*` (docs/10, spike 06). Revert to a single-region model id
  if a customer later needs UK-only processing.
- **Source:** spikes/06-uk-eea-data-residency.md; EU adequacy renewal (19 Dec 2025)
- **Reversible?:** cheap — a config change (`LLM_MODEL` id).

### D-016 — Extraction model: Claude Sonnet 4.6 for now (newer models account-gated)
- **Date:** 2026-11-10
- **Status:** accepted
- **Context:** Enabling Bedrock, the founder found only `eu.anthropic.claude-sonnet-4-6` and
  `eu.anthropic.claude-haiku-4-5` actually callable in `eu-west-2`. Sonnet 5, Sonnet 5.5 and
  Opus 5.5 all return "not available for this account" — an account-level entitlement, not a
  routing limit: the `global.*` profile returns the same error, confirming it is the account,
  not the geography.
- **Decision:** Use `eu.anthropic.claude-sonnet-4-6` for extraction now. It stays in the EU
  (D-015) and is strong at structured extraction.
- **Consequences:** The IAM inline policy `BedrockInvokeEuSonnet55` is scoped to this model's
  profile; its name is now stale but harmless. To request newer models, ask AWS Sales/Support for
  account `817210752440` (`eu-west-2`, model `eu.anthropic.claude-sonnet-5-5`) — limits usually
  relax as a new account builds billing history. When access opens, switching is a one-line
  `.env` change plus the IAM policy ARNs (docs/10).
- **Source:** Bedrock model-access test, 2026-11-10; [10-manual-steps.md](./10-manual-steps.md)
- **Reversible?:** cheap — a config change (`LLM_MODEL`) plus an IAM resource ARN.

### D-017 — H8 accuracy gate: containment metric for `job_type`, held-out `golden_v2`, frozen pass line (H8a)
- **Date:** 2026-11-13
- **Status:** accepted (2026-11-13). The founder reviewed and approved the `golden_v2` labels;
  the pass line is frozen from this date, before the gated run.
- **Context:** Hypothesis-table rule 1 says to freeze the pass line before the test starts. That
  did not happen for H8: the line was only ever "proposed" (docs/01, `scoring.py`), although
  `evals/README.md` and the `scoring.py` docstring said "frozen". The first scored run therefore
  happened without a freeze. Results on `golden_v1` (20 messages), with counts:

  | Prompt | `job_type` metric | `job_type` | `urgency` |
  |---|---|---|---|
  | `extract_v1` | exact match | 7/20 (0.35) | 16/20 (0.80) |
  | `extract_v2` | exact match | 12/20 (0.60); an earlier run scored 11/20 | 20/20 (1.00) |
  | `extract_v2` outputs, rescored | containment | 17/20 (0.85) | 20/20 (1.00) |
  | `extract_v3` | containment | 18/20 (0.90) | 20/20 (1.00) |

  Three problems with reading those numbers as evidence:
  1. **Tuned on the test set.** `extract_v2` and `extract_v3` were written after reading the
     misses on `golden_v1`, then scored on `golden_v1`. The 1.00 urgency score is optimistic.
  2. **The metric changed after the results.** Exact match on a free-text field measured wording,
     not usefulness: "decking installation" failed the label "decking". The remaining
     `job_type` misses under exact match were wording differences, with one real loss ("bespoke
     wardrobe" became "wardrobe installation", which dropped the word that matters).
  3. **Noise.** One message is 0.05 at 20 messages, and the same prompt scored 11/20 and 12/20.
- **Decision:**
  - `job_type` is scored by **containment**: every word of the label (lowercased, trailing "s"
    removed) must appear in the answer, and the answer may be at most **one word longer** than the
    label. Every other field stays exact match. `job_type` stays free text; no category list.
  - The gate is **H8a**, run on a new held-out set, `golden_v2` (40 messages, drafted from the
    labelling convention in `evals/README.md` without looking at model output). The gate is the
    **mean of three runs**, with counts reported. Pass line: `job_type` ≥ 0.80 and
    `urgency` ≥ 0.90, unchanged from H8. Prompt `extract_v3`, model
    `eu.anthropic.claude-sonnet-4-6` (D-016).
  - `golden_v1` stays as a regression guard. It is not gate evidence.
  - H8 keeps its recorded first-run result and is marked superseded (docs/01, rule 4).
  - The gate prints counts only; per-message answers go to `evals/reports/golden_v2.json` and
    are read after the gate is recorded. If the gate fails and the prompt is changed, `golden_v2`
    is spent as a held-out set and a third set is needed before claiming a pass.
- **Result (2026-11-13, one gated run: three passes over `golden_v2`, prompt `extract_v3`, model
  `eu.anthropic.claude-sonnet-4-6`):** PASS.

  | Run | `job_type` | `urgency` |
  |---|---|---|
  | 1 | 36/40 | 40/40 |
  | 2 | 35/40 | 40/40 |
  | 3 | 35/40 | 40/40 |
  | Mean | 0.883 (line ≥ 0.80) | 1.000 (line ≥ 0.90) |

  Other fields, mean: `name` 0.975, `location` 1.000, `preferred_date` 0.975. The set and prompt
  were not changed between freeze and run. Per-message detail:
  `evals/reports/golden_v2.json` (gitignored).
- **Consequences:** The pass tells us the extractor is not obviously broken on messages it was
  not tuned on. It does not tell us it is useful: 40 synthetic messages is a smoke test. The real
  H8 evidence is the Week 4 edit rate on live replies (#30, #35); until then the golden sets guard
  against regression only. One label in `golden_v1` ("kitchen worktop") breaks the "no rooms" rule;
  it stays as a known miss rather than being relabelled to fit the model. Rooms are dropped from
  `job_type` and are not stored in any field (a separate `room` field would be a schema change).
- **Source:** First scored runs, 2026-11-09 to 2026-11-13 (`evals/reports/`); hypothesis table
  rules 1, 2 and 4; Ries, *The Lean Startup* (2011), innovation accounting
- **Reversible?:** cheap — scoring constants and the dataset path, but changing the pass line after
  the gated run invalidates that run.

### D-018 — LLM provider locked: AWS Bedrock, `eu.anthropic.claude-sonnet-4-6` (R4)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** R4 (docs/05) is the risk that free LLM tiers train on customer data. AGENTS.md
  rule 5 requires a paid tier with a UK/EU DPA before live traffic. D-009 (ADR 0002) deferred the
  choice: stay provider-agnostic during the MVP, lock one DPA-backed provider before live traffic.
  The provider comparison lived in ADR 0002; D-015 and D-016 settled inference geography and model.
  The remaining step was the lock itself — confirming the DPA and paid tier, and recording them.
- **Decision:** Lock **AWS Bedrock** as the extraction provider, model
  `eu.anthropic.claude-sonnet-4-6` (D-016). The founder confirms the AWS DPA and UK transfer
  addendum are in place against the billed member account `817210752440`, which is pay-as-you-go
  (not a free tier). Bedrock carries AWS's contractual no-training commitment — inputs and outputs
  are not used to train the models — so R4's exposure is closed. The synthetic-data-only rule is
  unchanged: it runs until the live gate, not until this decision.
- **Consequences:**
  - R4 moves from "open — deferred to #29" to mitigated (docs/05). Re-confirm the DPA copy is
    kept and the account remains paid before the first live message; that re-check rides with the
    deployment gate (#29, "paid tier + DPA in place").
  - No code change. The Bedrock adapter, `extract_v3` prompt, and the H8a gate already run on
    this exact model, so the lock records what the repo already does rather than changing it.
  - The provider seam (`build_llm`) stays. A future model or provider switch is a config change
    plus a golden-set re-run against the new model (ADR 0002), not a schema change.
- **Source:** Founder confirmation, 2026-11-13; ADR 0002 (D-009); D-015, D-016;
  [Amazon Bedrock data protection](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)
  (no training on inputs/outputs).
- **Reversible?:** cheap — the seam keeps providers swappable; re-locking another provider means
  re-running the golden set against it.

### D-019 — HELP/STOP opt-out: handle ourselves, confirm STOP and reply HELP (fixed templates)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** Twilio's GB SMS guidance expects `HELP`/`STOP` support. The fixed missed-call
  template (D-004) had neither, so a caller had no documented way to opt out; #72 tracked it. The
  repo sends from a Twilio UK long code, which Twilio's free opt-out handling does not cover, so
  the real choice was self-handle versus Twilio's paid Advanced Opt-Out.
- **Decision:**
  - **Handle opt-out ourselves**, not Twilio Advanced Opt-Out: one service, one Postgres (D-005),
    the state stays visible, and no per-number add-on cost. An `opt_outs` table keyed on
    `caller_number` records the opt-out; a caller is matched on the exact normalised body.
  - **Confirm STOP and answer HELP**, each with a fixed one-line template (D-004: the AI never
    writes free text). STOP confirms the opt-out; HELP repeats the "reply with name / job /
    where" instruction.
  - **Opt-out suppresses the auto-text, never the record.** A missed call from an opted-out number
    is still stored in `raw_events`, so the tradesperson sees it and can ring back; no lead is
    silently lost. Suppression applies only to the SMS.
  - Keywords: `STOP`, `STOPALL`, `UNSUBSCRIBE`, `CANCEL`, `END`, `QUIT` opt out; `HELP` asks for
    help. Matching is case- and whitespace-insensitive, and only the exact keyword matches, so a
    normal reply like "help fix the tap" is untouched.
- **Consequences:**
  - `sms_reply` handles STOP/HELP before extraction, so they never reach the LLM or produce a job
    row. A STOP records the opt-out idempotently; a duplicate delivery confirms nothing twice.
  - `missed_call` checks `opt_outs` before scheduling the text.
  - New migration `0005` (`opt_outs`), a `db/opt_out.py` module, and tests covering idempotency,
    the STOP/HELP templates, and the "no second auto-text after STOP" guarantee.
- **Source:** Founder decision, 2026-11-13; Twilio GB SMS guidelines; D-004, D-005.
- **Reversible?:** cheap — delete a table and two webhook branches. Re-adopting Twilio Advanced
  Opt-Out later is possible but moves state out of Postgres.

### D-020 — Production hosting: AWS App Runner (containers) for the stateless API (#29)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** #29 (deployment) needed a home for the stateless FastAPI app. Spike 07 compared
  Vercel, AWS App Runner, ECS Fargate, Fly.io, Render and Railway against the workload's real
  constraints, not platform marketing. Two requirements rule out serverless: the in-process
  `BackgroundTasks` (extraction + SMS send run after the 200, in the same process) and LangGraph
  `interrupt()` (D-008, a human-approval run is held and resumed by a live process). Vercel runs
  Python/FastAPI but its serverless model reclaims the process after the response, cutting off
  exactly that work.
- **Decision:** Host the API on **AWS App Runner** — managed, long-running containers, no
  Kubernetes. The database stays Supabase (docs/05) and the LLM stays Bedrock (D-018); this
  decision is only the stateless app layer. Rationale: a long-running process fits the code as
  written, it is the same AWS account as Bedrock (one bill, one IAM story), and the Activate
  credits offset hosting. Fly.io and Render are the accepted fallback.
- **Consequences:**
  - New `Dockerfile` and `.dockerignore`; an ECR repository; an App Runner service with a
    `/ready` readiness check (DB connectivity) alongside the existing `/health`.
  - Bedrock auth moves from `AWS_PROFILE` (`~/.aws/credentials`) to an **App Runner instance
    role** with the Bedrock invoke permission — boto3's default credential chain picks up the
    role, so no AWS keys live in the container.
  - Secrets (Twilio, `DATABASE_URL`) are injected as App Runner environment variables, sensitive
    values referenced from Secrets Manager. Migrations run against Supabase as a separate step.
  - The app is stateless and Dockerized, so moving to Fly.io or Render later is a config change,
    not a rewrite (spike 07).
- **Source:** Founder decision, 2026-11-13; spike 07; docs/04 (Activate credits), D-005, D-008,
  D-018.
- **Reversible?:** cheap — the app is host-agnostic; a move is a deploy-config swap plus re-pointing
  the same env vars. The sticky choices (Supabase, Bedrock) are orthogonal and unchanged.

### D-021 — Outbound SMS is persisted (`outbound_messages`) with status callbacks and retention (#73)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** Outbound SMS was only logged (`logger.info("sms %s accepted")`), never stored.
  The product promise is "your missed call gets a text", and we could not prove per call that it
  happened, nor see delivery failures without opening Twilio. The reply-rate metric (H6) also
  needs a denominator of "texts actually sent". #73 tracked it.
- **Decision:**
  - Persist every outbound SMS in a new `outbound_messages` table: `twilio_message_sid` (unique,
    null until Twilio accepts), `raw_event_id` (the triggering inbound event — the missed call
    for the auto-text, or the STOP/HELP reply for a confirmation/help), `to`, `body`, `status`,
    `error_code`, `sent_at`.
  - Write the row **before** the Twilio call (the outbound analogue of persist-before-processing),
    then update it with the SID or the error code. A send failure records `status='failed'` plus
    `error_code` (e.g. `21211`), with no SID.
  - Twilio's delivery-status callback (`POST /webhooks/sms-status`) updates the row to
    `delivered`/`undelivered`/`failed`, idempotently. The callback URL is passed per message from
    `PUBLIC_BASE_URL`.
  - **Retention:** `to` and `body` are personal data, so retain them for **30 days**, then purge
    them (keep `twilio_message_sid` and `status` for aggregate metrics). The purge automation
    rides with #34; the decision is recorded now so the field isn't treated as free to keep.
- **Consequences:**
  - "Was this caller texted, and did it deliver?" is answerable from our own database.
  - A reply is linked to the specific text that prompted it via `raw_events.related_event_id` →
    `outbound_messages.raw_event_id` (`find_outbound_for_reply`); no redundant column on
    `raw_events`.
  - Migration `0006`; the send path now takes a session factory like `extract_reply`, so a
    background send opens its own session.
- **Source:** #73; founder decision 2026-11-13; D-005 (persist before processing); R4/D-018 (DPA).
- **Reversible?:** cheap — drop a table and the callback route. The only irreversible part is the
  retention decision, which is a policy line, not a schema constraint.

### D-022 — Business metrics frozen: capture rate, reply rate, jobs booked, edit rate (#30)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** #30 asked for "capture rate, reply rate, jobs booked, edit rate". docs/01's
  definitions were deliberately loose ("missed calls that produced a stored record", "human edits
  ÷ AI-produced job records"). A metric must be frozen *before* it is read, or its line can be
  moved after seeing results (Ries — the docs/01 anti-pattern). D-021 made "texts sent"
  queryable, so the reply-rate denominator can finally be real rather than "missed calls".
- **Decision:** freeze the exact counts, computed in `agent_ant_core/metrics.py`:
  - **capture_rate** = `job_records ÷ voice_calls` — jobs captured per missed call. Every
    `job_records` row counts as captured (extraction wrote it), whatever its later status.
  - **reply_rate** = `sms_replies ÷ outbound_messages` — replies per auto-text sent. Gates H6.
  - **jobs_booked** = `count(job_records WHERE status='approved')` — a count, the money metric.
  - **edit_rate** = `distinct jobs with ≥1 human_edit ÷ job_records` — corrections per AI job, the
    LLM-drift alarm.
  - Each rate is `0.0` when its denominator is empty.
- **Consequences:**
  - Exposed on the dashboard (server-rendered, D-014) as counts plus percentages, e.g.
    "3 jobs / 10 missed calls (30%)".
  - **H6's reply-rate threshold is still not frozen.** The issue's second box ("freeze after the
    first live week") is deferred: `reply_rate` is computed now, but no pass line exists until
    there is a live week to set it from.
  - Accepted caveat: `capture_rate` counts every `job_records` row, and a reply with no missed
    call (a caller texting the number directly) still produces a job, so the ratio can exceed 1.0
    in theory. Harmless at MVP volume.
- **Source:** #30; docs/01 metric definitions; Ries, *The Lean Startup* (2011), innovation accounting.
- **Reversible?:** cheap — the definitions are one module. Changing any of them after the first
  live read invalidates that read, so supersede instead (append a new entry).

### D-023 — Retry policy: failed SMS sends retried up to 3 attempts, then dead-lettered (#34)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** #34 (hardening). A failed SMS send was recorded (D-021) but never retried, and
  nothing surfaced it except a log line. The blocker to G0b is trust — Dad will not forward his
  livelihood's calls to something that can silently drop a text — so a failed send must be visible
  and recoverable.
- **Decision:**
  - A failed send (`status='failed'`) is retried up to **3 attempts** (including the first) via
    `just retry-sms`; each retry bumps `outbound_messages.attempts`.
  - After the bound, it is **dead-lettered** (`status='dead'`) and listed on the dashboard's
    failure panel for manual handling.
  - The retry is a command, not automatic — schedule it (cron / App Runner scheduled job) at
    deploy. The dashboard panel is the MVP "alert"; email/Slack alerting is deferred to a later
    #34 slice. Extraction failures are retried separately, also later.
- **Consequences:** `outbound_messages.attempts` (migration 0007), `retry_failed_sends` and
  `list_failed_messages` in `db/outbound_sms.py`, `scripts/retry_sms.py` + `just retry-sms`, and a
  dashboard failure panel.
- **Source:** #34; founder decision 2026-11-13; D-021.
- **Reversible?:** cheap — `MAX_SEND_ATTEMPTS` is one constant.

### D-024 — Retry policy: failed extractions retried up to 3 attempts, then dead-lettered (#34)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** #34 (hardening). A failed extraction — invalid output after its bounded repairs, or a
  raised provider call — was swallowed by the background task: the invalid case left only an audit
  row, the raised case left nothing but a log line. Neither was ever retried, and an extraction
  failure is the higher-stakes gap of the two (a lost *lead*, versus a lost auto-text). Same trust
  argument as D-023, now for the job itself.
- **Decision:**
  - `raw_events` gains `extraction_attempts` (default 0) and `extraction_status` (`done` /
    `failed` / `dead`; `NULL` = never attempted). Voice calls are never extracted, so they stay
    0 / `NULL`.
  - Every attempt — the background task's first run included — bumps `extraction_attempts` and
    records `done` (a job was captured) or `failed` (invalid, or the provider raised). A raised
    call is rolled back and re-marked `failed` in a fresh transaction, so an outage surfaces as a
    retryable row instead of vanishing.
  - `retry_failed_extractions` (`just retry-extractions`) re-runs extraction over every reply that
    is not `done` and under `MAX_EXTRACTION_ATTEMPTS` (3); a reply still `failed` at the bound is
    promoted to `dead` and shown on the dashboard's failure panel.
  - Idempotency is unchanged: `persist_job_record` (`INSERT … ON CONFLICT DO NOTHING`) means a
    concurrent retry cannot create a second job.
- **Consequences:** migration 0008; `db/extraction.py` (`candidate_replies`,
  `list_failed_extractions`); `extraction.py` (`_extract_one`, `retry_failed_extractions`);
  `scripts/retry_extractions.py` + `just retry-extractions`; the dashboard "failed extractions"
  panel.
- **Source:** #34; D-023 (the SMS analogue); founder decision 2026-11-13.
- **Reversible?:** cheap — `MAX_EXTRACTION_ATTEMPTS` is one constant.

### D-025 — Retention purge: outbound personal fields redacted at 30 days; wider retention deferred (#34)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** D-021 fixed the 30-day line for `outbound_messages.to`/`body` but left the purge
  automation to #34. The wider question — how long to keep `raw_events.payload` and
  `job_records.raw_message`, which also carry caller numbers and message bodies — is *not*
  answered by D-021 and cannot be assumed to be 30 days.
- **Decision:**
  - `purge_personal_data` (`just purge`) clears `outbound_messages.to` and `body` (sets to `""`)
    once a row is older than 30 days, keeping the SID, status, error code and timestamps for
    aggregate metrics. Idempotent: already-redacted rows are skipped.
  - The wider retention of `raw_events`, `job_records` and `llm_output_audits` is **deferred** to a
    separate founder decision (D-0xx): those tables are the business data itself — the job record
    is the product, not an operational log — so a blanket 30-day purge would destroy the record of
    work done.
- **Consequences:** `purge_personal_data` in `db/outbound_sms.py`; `scripts/purge_old_data.py` +
  `just purge`; scheduled alongside the retry commands.
- **Source:** #34; D-021; founder decision 2026-11-13.
- **Reversible?:** cheap — a constant and a script. (The redaction itself is one-way for the row,
  which is the point.)

### D-026 — Support alerting via Slack incoming webhook (operator, not customer) (#94)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** D-023 and D-024 made failures *visible* on the dashboard but not *pushed*: the
  founder would have to open the dashboard to notice a failed send or a dead-lettered extraction.
  The dashboard is the tradesperson's surface; infra failures are the *operator's* job (provider
  down, retry queue filling) and pushing them to the tradesperson would confuse him. The founder
  asked where alerts land and split the channels himself: he wants system logs/alerts in Slack,
  and will use WhatsApp (or in-app chat) for *client* conversations later.
- **Decision:**
  - Support alerts go to **Slack via an incoming webhook** (`SLACK_WEBHOOK_URL`, a `SecretStr`).
    Unset = no-op, so local dev stays quiet.
  - Two alert types, both in background tasks / scheduled scripts (never the webhook hot path):
    an SMS send failure, and a dead-lettered extraction (needs manual filing).
  - Alert text carries a SID/number, never a message body or caller number (rule 5), and points
    the operator at the dashboard. `post_to_slack` swallows all errors — alerting must never take
    down the thing it watches.
  - Customer-facing conversation stays a *separate, later* product decision: WhatsApp or in-app
    chat, not Slack.
- **Consequences:** `apps/api/src/agent_ant_api/notify.py` (`post_to_slack`, `make_notifier`,
  `notify_support`); `slack_webhook_url` on `Settings`; `SLACK_WEBHOOK_URL` in `.env.example`;
  `just test-slack` (`scripts/test_slack.py`); wired into `sms.py` (send failure) and
  `extraction.py` (dead-letter).
- **Source:** #94; founder decision 2026-11-13.
- **Reversible?:** cheap — remove the webhook URL and the notifier is a no-op.

### D-027 — Retention + erasure: raw/audit data redacted at 90 days, job records kept, on-request erase (#95)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** D-025 redacted outbound `to`/`body` at 30 days but deliberately left the wider
  question open: `raw_events.payload`/`caller_number` and `llm_output_audits.raw_output` still carry
  caller numbers and message text, held forever. The same question splits into two jobs — a
  time-based schedule (how long may the *operational* logs keep personal data) and a request-based
  erasure (the caller asks to be forgotten).
- **Decision:**
  - `raw_events.payload` and `raw_events.caller_number` are **redacted (blanked, not deleted) after
    90 days**, as is `llm_output_audits.raw_output`. 90 days is long enough to replay a failed
    extraction and debug, short enough to be defensible. The idempotency key, `source`, timestamps,
    status and attempt counts survive, so dedupe and metrics keep working.
  - A reply still retryable (extraction never ran, or last failed) is skipped by the purge: blanking
    its body would turn a recoverable lead into an empty guaranteed dead-letter.
  - `job_records` (including `raw_message`, the caller's exact words) and `human_edits` are **kept
    for as long as the caller is a customer**. They are the tradesperson's business record — the
    product, not an operational log — and keep the original wording for reviewing edits. A blanket
    purge would destroy the record of work done.
  - **Erasure on request** (`just erase <number>`, E.164) clears one caller's number, message text
    and identifying extracted fields (`name`, `location`, `preferred_date`) across `raw_events`,
    `outbound_messages`, `job_records` and `llm_output_audits`, keeping the operational skeleton so
    counts stay coherent. The tradesperson's own corrections (`human_edits`) are not erased with the
    caller — they are the operator's action trail.
- **Consequences:** `db/retention.py` (`redact_raw_events`, `redact_llm_outputs`, `erase_person`);
  `scripts/purge_old_data.py` now covers raw/audit on top of outbound; `scripts/erase_person.py` +
  `just erase <number>`; scheduled alongside the other purge/retry commands.
- **Source:** #95; founder decision 2026-11-13.
- **Reversible?:** cheap for the *policy* (three constants), one-way for an already-redacted row —
  which is the point.

### D-028 — Schedule the retry and purge commands via CDK (EventBridge Scheduler → ECS Fargate) (#96)
- **Date:** 2026-11-13
- **Status:** accepted
- **Context:** D-023, D-024 and D-025 made recovery and retention *commands* (`just retry-sms`,
  `retry-extractions`, `purge`) but left the scheduling to "at deploy". App Runner (D-020) has no
  native cron, so without something to trigger them a failed send or extraction sits `failed`
  forever and outbound `to`/`body` age past 30 days. The founder asked for the scheduler to be
  committed as code rather than hand-documented console steps, so it is reviewable and cannot
  drift.
- **Decision:**
  - Express the scheduler as a **CDK app** in `infra/cdk/` — a standalone uv project, not a
    workspace member — that creates three **EventBridge Scheduler** schedules, each running a
    one-off **ECS Fargate** task on the same image as the API: `retry-sms` and
    `retry-extractions` every ~5 minutes (configurable `retryRateMinutes`), `purge` daily at
    03:00 UTC.
  - One task definition per script: EventBridge Scheduler's ECS target cannot override a
    container's command, so the command is baked into the task definition.
  - Adopt CDK as the IaC tool **for this stack only**; App Runner, ECR and IAM stay hand-managed
    (D-020) until a separate decision migrates them. A one-time `cdk bootstrap` is a prerequisite.
  - Two #96 gaps are folded in: a fully dead-lettered SMS send now alerts the operator via Slack
    (D-026) through an `on_dead_letter` callback on `retry_failed_sends` → `alert_dead_letter`,
    and the dashboard's failed-extractions panel shows the reply body so a dead lead can be read
    without opening the database.
  - The `Dockerfile` now copies `scripts/` into the image, so the scheduled tasks can run them.
- **Consequences:**
  - The schedules are reviewable, drift-checked (`cdk diff`) and applied with
    `just cdk-synth`/`cdk-diff`/`cdk-deploy`, passing account-specific values as `-c key=value`
    (secrets referenced by Secrets Manager ARN, never committed).
  - The Fargate tasks run in the VPC's **public** subnets with a public IP — the pre-live tradeoff
    that avoids NAT and VPC endpoints; revisit before real traffic.
  - A lone CDK app for three schedules is a half-migration: it will nag until App Runner/ECR join
    it, and it adds a Node-CLI + `aws-cdk-lib` toolchain that sits outside the workspace.
  - `core` still does not import the app layer: the dead-letter hook is a `Callable` passed in, so
    the dependency direction (apps → agents → core) holds.
- **Source:** #96; founder decision 2026-11-13; D-020, D-023, D-024, D-025, D-026.
- **Reversible?:** cheap — `cdk destroy` removes the schedules; the task definitions and roles are
  new.

## Anti-patterns

- ⚠️ **Editing history.** Rewriting an entry hides why a choice was made. Supersede it instead.
- ⚠️ **Decisions with no source.** If it cannot cite a doc, interview or measurement, it is
  an opinion — mark it `proposed`.
- ⚠️ **Recording only the choice.** Without context and consequences, the entry cannot be
  re-evaluated when conditions change.

## Open questions

- Which beachhead segment (carpenters nationally or one region)? See issue #15. Deferred by D-010;
  working assumption is tradespeople in general until then.

## Change history

- **0.21 (2026-11-13)** — D-028 accepted: the retry and purge commands are scheduled via a CDK
  app (`infra/cdk/`) — EventBridge Scheduler → ECS Fargate — and the dead-letter alert + reply
  body on the failure panel are folded in (#96).
- **0.20 (2026-11-13)** — D-027 accepted: 90-day redaction for `raw_events` + `llm_output_audits`,
  `job_records`/`human_edits` kept as the business record, and on-request `just erase <number>` (#95).
- **0.19 (2026-11-13)** — D-026 accepted: support alerts go to Slack via an incoming webhook
  (operator-only); WhatsApp/in-app chat stays a later customer-channel decision (#94).
- **0.18 (2026-11-13)** — D-024 and D-025 accepted: failed extractions retried then dead-lettered,
  and the 30-day outbound purge automated (wider retention deferred). Completes #34.
- **0.17 (2026-11-13)** — D-023 accepted: failed SMS sends retried up to 3 attempts then
  dead-lettered, with a dashboard failure panel (#34).
- **0.16 (2026-11-13)** — D-022 accepted: the four business metrics frozen and exposed on the
  dashboard (#30).
- **0.15 (2026-11-13)** — D-021 accepted: outbound SMS persisted with status callbacks and a
  30-day retention line for personal fields (#73).
- **0.14 (2026-11-13)** — D-020 accepted: AWS App Runner for the stateless API (spike 07).
- **0.13 (2026-11-13)** — D-019 accepted: HELP/STOP opt-out handled ourselves (confirm STOP,
  reply HELP), recorded as the pre-live-traffic decision for #72.
- **0.12 (2026-11-13)** — D-018 accepted: Bedrock locked as the DPA-backed provider
  (`eu.anthropic.claude-sonnet-4-6`), closing R4's "free tier" exposure.

- **0.11 (2026-11-13)** — D-014 accepted (decided 2026-11-09): the HITL dashboard lives
  in the API, server-rendered. Landed after #28's branch missed `main`.
- **0.10 (2026-11-13)** — D-017 accepted: containment metric for `job_type`, held-out
  `golden_v2`, and the H8a pass line, recorded as a change made after the first scored run.
  Gated run recorded: PASS (`job_type` 0.883, `urgency` 1.000).
- **0.9 (2026-11-10)** — D-016 accepted: extraction uses `eu.anthropic.claude-sonnet-4-6` for now;
  newer Claude models are account-gated for `817210752440`, not blocked by routing.
- **0.8 (2026-11-10)** — D-015 accepted: `eu.*` cross-region inference is acceptable (stays in EU
  geography); `global.*` stays rejected. Relaxes D-009's single-region constraint.
- **0.7 (2026-11-09)** — D-013 accepted: `job_records` table and background extraction wire a
  reply into a captured job + audit row; the approval interrupt stays Week 4.
- **0.6 (2026-11-09)** — D-012 accepted: audit trail is two tables (`llm_output_audits` +
  `human_edits`) with `job_id` deferred until `job_records` exists (#23).
- **0.5 (2026-11-07)** — D-011 accepted: auto-SMS sent from the Twilio number with the business
  name in the template; revisit on a low reply rate.
- **0.4 (2026-11-07)** — D-010 accepted: Week 1 build starts before G0a, G0b and the beachhead
  decision, on the founder's say-so.
- **0.3 (2026-11-05)** — D-008 and D-009 accepted on the founder's decision: LangGraph rather
  than plain steps, and a swappable LLM provider with Bedrock preferred and a DPA-backed lock
  before live traffic.
- **0.2 (2026-11-04)** — D-008 expanded and linked to its ADR; D-009 added for the LLM provider
  and DPA decision; both remain `proposed` pending founder sign-off.
- **0.1 (2026-11-04)** — created with seed entries D-001 to D-008.
