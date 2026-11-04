# 0001 — Orchestration: LangGraph for the missed-call agent

- **Status:** accepted
- **Date:** 2026-11-05
- **Decision log entry:** D-008

## Context

The MVP flow looks linear on paper: receive → extract → validate → persist → notify → human
review. In practice it already has three branch points (valid vs. invalid extraction, repair
attempts exhausted, human approves/edits/rejects), and it is expected to become multi-turn once
callers reply more than once.

The first draft of this ADR recommended plain Python functions and deferred LangGraph. The
founder rejected that: the orchestration model should be in place before the flow grows, so the
branching and human-in-the-loop handling do not have to be retrofitted under time pressure.

Constraints that still apply:

- **D-005** — one service, one Postgres, no broker. LangGraph must not introduce a second
  runtime or a queue.
- **D-003** — one agent. The graph is for `missed_call` only.
- **Testability** — nodes must stay thin enough to unit-test without a live model.
- **G0c item 5** — build a state graph with one conditional branch. This is now on the critical
  path rather than deferred.

## Options considered

| Option | Outcome |
|---|---|
| **LangGraph** (chosen) | Explicit `StateGraph`, conditional edges, a Postgres checkpointer for resumability, and `interrupt()` for human-in-the-loop. Costs a learning curve and a dependency |
| Plain functions + Pydantic | Simpler today, but branching and resume logic would be hand-rolled and then migrated |
| Durable workflow engine (Temporal, Hatchet, Prefect) | Real durability, but a second service to operate — contradicts D-005 |
| Hand-rolled state machine table | Explicit, but re-implements what LangGraph already provides |

## Decision

**Use LangGraph for the `missed_call` agent, starting in Week 2.**

Shape of the graph:

```
ingest → extract → validate ──valid──→ persist → notify → await_human → done
                      │
                      └──invalid──→ repair ──ok──→ validate
                                      └──exhausted──→ needs_review
```

- **Checkpointer:** Postgres (`langgraph-checkpoint-postgres`), so state survives a restart
  without adding Redis or a broker. This keeps D-005 intact; it adds tables, not services.
- **Human-in-the-loop:** `interrupt()` at `await_human`, resumed when Dad approves, edits or
  rejects. The approval still writes to the same `job_records` row.
- **Dependency location:** `agents/missed_call` only. `packages/core` stays framework-free so
  shared code does not inherit LangGraph's release cadence.
- **Thin nodes:** each node calls a plain function. Business logic, prompts and Pydantic models
  live outside the graph, which keeps them unit-testable and makes a future migration possible.
- **No LangServe, no LangGraph Platform.** Hosting stays one FastAPI service.

## Consequences

**Easier:** branching is declarative; resumability and interrupts come from the framework
instead of custom code; the flow diagram in doc 05 maps directly onto the graph; adding a second
turn later is a new node and edge, not a redesign.

**Harder / accepted:**

- A framework to learn and debug. Graph tracebacks are less direct than a Python stack, so nodes
  stay small and logging is per-node.
- Version churn: pin `langgraph` and `langgraph-checkpoint-postgres`, and upgrade deliberately.
- Checkpoint tables need an Alembic migration alongside the domain schema.
- Tests need a graph harness for the wiring, plus plain unit tests for the node functions.
- Risk of over-modelling: if the graph passes ~10 nodes for this flow, that is a signal the
  abstraction is being used for its own sake.

**Knock-on changes:**

- [07-learning-track.md](../07-learning-track.md): the LangGraph row moves up to sit immediately
  after structured output, before evaluation.
- [05-architecture-and-schema.md](../05-architecture-and-schema.md): G0c item 5 is active again.
- The earlier plain-Python proposal is not kept as a superseded ADR because it was never merged
  or accepted; this file is its replacement.

## Source

- [05-architecture-and-schema.md](../05-architecture-and-schema.md) — orchestration, D-005
- Founder decision, 2026-11-05 (rejecting the plain-steps recommendation)
- Huyen — *AI Engineering* (2025) — cap autonomy, human on consequential actions
- LangGraph documentation, checked 2026-11-04 — `StateGraph`, checkpointers, `interrupt()`
