---
title: Decision Log
status: draft
version: 0.3
last_updated: 2026-11-05
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
- **Consequences:** R4 stays open until Week 4 — the risk being carried. Mitigations are the
  synthetic-data rule and the explicit gate. An adapter seam keeps a switch to a config change.
  Real customer messages arriving early must not be sent to the LLM.
- **Source:** [adr/0002-llm-provider.md](./adr/0002-llm-provider.md)
- **Reversible?:** cheap by design — that is the point of the decision.

## Anti-patterns

- ⚠️ **Editing history.** Rewriting an entry hides why a choice was made. Supersede it instead.
- ⚠️ **Decisions with no source.** If it cannot cite a doc, interview or measurement, it is
  an opinion — mark it `proposed`.
- ⚠️ **Recording only the choice.** Without context and consequences, the entry cannot be
  re-evaluated when conditions change.

## Open questions

- Which beachhead segment (carpenters nationally or one region)? See issue #15.
- Which provider wins the Week 4 lock-in? Decide on the golden set and the DPA, at gate #29.

## Change history

- **0.3 (2026-11-05)** — D-008 and D-009 accepted on the founder's decision: LangGraph rather
  than plain steps, and a swappable LLM provider with Bedrock preferred and a DPA-backed lock
  before live traffic.
- **0.2 (2026-11-04)** — D-008 expanded and linked to its ADR; D-009 added for the LLM provider
  and DPA decision; both remain `proposed` pending founder sign-off.
- **0.1 (2026-11-04)** — created with seed entries D-001 to D-008.
