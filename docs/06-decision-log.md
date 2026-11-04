---
title: Decision Log
status: draft
version: 0.1
last_updated: 2026-11-04
sources:
  - Nygard — Documenting Architecture Decisions (ADR format) ⚠️ TO CHECK
  - Ries — The Lean Startup (validated learning) ⚠️ TO CHECK
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
| D-008 | Orchestration: plain Python steps, not LangGraph | proposed | 2026-11-04 |

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
- **Source:** Huyen — AI Engineering (agent autonomy) ⚠️ TO CHECK; [00-business-plan.md](./00-business-plan.md) §5
- **Reversible?:** cheap, but revisit only with evidence from live data.

### D-005 — One service, one Postgres, no broker
- **Date:** 2026-11-04
- **Status:** accepted
- **Context:** A solo founder at ~2 hrs/day cannot operate distributed infrastructure.
- **Decision:** One FastAPI service, one Postgres (Supabase), FastAPI background tasks. No
  Kafka, no queue broker, no microservices.
- **Consequences:** Durability relies on persisting the raw event first. A crash mid-task is
  recovered by reprocessing stored events.
- **Source:** Kleppmann — DDIA ⚠️ TO CHECK; [05-architecture-and-schema.md](./05-architecture-and-schema.md)
- **Reversible?:** costly once real traffic and data exist.

### D-006 — Dad goes live in Week 4
- **Date:** 2026-11-04
- **Status:** accepted
- **Context:** v0.1 had Dad live in Week 6, giving one week of real data.
- **Decision:** Go live text-only in Week 4, for three weeks of real data.
- **Consequences:** Hardening is compressed; the Week 4 gate carries more weight.
- **Source:** Ries — The Lean Startup (shorten the loop) ⚠️ TO CHECK; [00-business-plan.md](./00-business-plan.md) §7
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

### D-008 — Orchestration: plain Python steps, not LangGraph
- **Date:** 2026-11-04
- **Status:** proposed — awaiting founder sign-off (issue #14)
- **Context:** The MVP flow is linear: receive → extract → validate → confirm.
- **Decision (proposed):** Plain functions plus Pydantic. Introduce LangGraph only if the
  conversation becomes genuinely multi-turn with branching.
- **Consequences:** The LangGraph precursor item drops in priority in
  [07-learning-track.md](./07-learning-track.md).
- **Source:** [05-architecture-and-schema.md](./05-architecture-and-schema.md) — Orchestration
- **Reversible?:** cheap

## Anti-patterns

- ⚠️ **Editing history.** Rewriting an entry hides why a choice was made. Supersede it instead.
- ⚠️ **Decisions with no source.** If it cannot cite a doc, interview or measurement, it is
  an opinion — mark it `proposed`.
- ⚠️ **Recording only the choice.** Without context and consequences, the entry cannot be
  re-evaluated when conditions change.

## Open questions

- Which beachhead segment (carpenters nationally or one region)? See issue #15.
- Which paid LLM tier and DPA? See issue #16.

## Change history

- **0.1 (2026-11-04)** — created with seed entries D-001 to D-008.
