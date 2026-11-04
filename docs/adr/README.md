# Architecture Decision Records

Longer-form decisions that do not fit in a single entry in [the decision log](../06-decision-log.md).

## When to write an ADR

Write one when a decision needs real alternatives and trade-offs, for example LangGraph vs.
plain Python steps. Small decisions stay in the decision log only.

## Rules

- Files are named `NNNN-short-title.md`, numbered from `0001`.
- Every ADR gets an entry in the decision log that links to it.
- ADRs are append-only. To change one, write a new ADR and mark the old one superseded.
- Copy [template.md](./template.md) to start.
