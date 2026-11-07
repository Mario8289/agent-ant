---
title: Learning Track
status: draft
version: 0.4
last_updated: 2026-11-06
sources:
  - Lubanovic — FastAPI: Modern Python Web Development (O'Reilly, 2024) — verified
  - Huyen — AI Engineering (O'Reilly, 2025) — verified
  - Kleppmann & Riccomini — Designing Data-Intensive Applications, 2nd ed. (2026) — verified
---

# 07 — Learning Track

## Purpose

The skills needed before and during the 6-week sprint, in the order they unblock work. Each
skill has a "done when" test so learning is measured by something working, not by hours
spent. It mirrors the Precursor Ready Check (gate G0c) in
[05-architecture-and-schema.md](./05-architecture-and-schema.md).

Budget: ~2 hrs/day. Learning that does not unblock a sprint deliverable waits.

## Track

| Order | Skill | Unblocks | Done when | Resource |
|---|---|---|---|---|
| 1 | FastAPI: async handlers, **form-encoded** webhooks, background tasks | G0c item 1, W1.1 | A local endpoint accepts a form-encoded POST and returns valid TwiML | Lubanovic — FastAPI (chapters TBD) |
| 2 | Twilio: numbers, webhooks, signature verification, conditional forwarding | G0b, G0c item 3, W1.1, W1.3 | A forwarded unanswered call hits the webhook on Dad's carrier | Twilio docs (verify) |
| 3 | Postgres from Python: SQLAlchemy/Alembic, unique constraints, transactions | G0c item 4, W1.2 | A duplicate insert on `idempotency_key` is rejected and handled | Kleppmann — DDIA (relevant chapters TBD) |
| 4 | Structured LLM output: Pydantic validation, repair loop | G0c item 2, W2.1, W2.2 | Messy text becomes a validated object; invalid output triggers bounded repair | Pydantic docs — official tutorial (docs.pydantic.dev) · Huyen — AI Engineering (chapters TBD) |
| 5 | LangGraph: `StateGraph`, conditional edges, Postgres checkpointer, `interrupt()` | G0c item 5, W2.1, W4.1 | A synthetic message runs extract → validate → interrupt → approve, and resumes from the checkpoint | LangGraph docs |
| 6 | Evaluation: golden sets, scoring, threshold-setting | W3.1, W3.2 | `just eval` reports accuracy against a hand-labelled set | Huyen — AI Engineering |
| 7 | Human-in-the-loop and drift monitoring: audit tables, edit rate | W2.3, W4.1, W4.3 | Edit rate can be queried from stored human edits | Huyen — AI Engineering |

## Rules

1. Learn the next row only when the current row's "done when" passes, or when it is no longer
   on the critical path.
2. Prefer building the real thing (the sprint deliverable) over a toy exercise.
3. Note what surprised you in the change history so the track improves.

## Anti-patterns

- ⚠️ **Learning ahead of need.** Rows 5–7 are not worth starting before gates G0a and G0b
  pass. If discovery fails, the build does not happen.
- ⚠️ **Course completion as progress.** A certificate tests nothing (Ries — vanity metric).
- ⚠️ **Tutorials with no connection to the product.** Use the missed-call flow as the exercise.

## Open questions

- Which specific chapters and courses go in the remaining Resource cells (rows 1–3, 6–7)? Row 4's
  Pydantic course is set (docs.pydantic.dev).
- ~~Does the LangGraph row stay deferred?~~ No — LangGraph is now row 5, ahead of evaluation
  ([D-008](./06-decision-log.md)).

## Change history

- **0.4 (2026-11-06)** — named the Pydantic course (official tutorial, docs.pydantic.dev) as the
  Resource for row 4, alongside Huyen.
- **0.3 (2026-11-05)** — LangGraph moved from a deferred row to row 5, ahead of evaluation;
  scope expanded to the Postgres checkpointer and `interrupt()`.
- **0.2 (2026-11-04)** — LangGraph row tied to ADR 0001's re-evaluation triggers rather than to
  a bare decision ID.
- **0.1 (2026-11-04)** — created from the Precursor Ready Check and the sprint plan.
