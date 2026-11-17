---
id: D-007
title: "Python-first `uv` workspace monorepo, `agent_ant_*` naming"
status: accepted
date: 2026-11-04
---

# D-007 — Python-first `uv` workspace monorepo, `agent_ant_*` naming

- **Date:** 2026-11-04
- **Status:** accepted
- **Reversible?** costly once many packages exist; cheap now.

## Context

The repo must hold multiple agents and products without becoming a tangle.

## Decision

- `uv` workspace with `apps/` (deployables), `agents/` (one package per agent) and
  `packages/` (shared libraries). Dependencies point one way: apps → agents → core.
- Python packages are named `agent_ant_*`.
- Tooling: `ruff`, `pyright`, `pytest`, `just`, Alembic.
- `apps/dashboard` is a placeholder until Week 4.
- Prompts are versioned files; evals live in `evals/`, separate from unit tests.

## Consequences

Slightly more files up front than a single package; cheaper to add a
second agent or product later.

## Source

Planning discussion 2026-11-04; tracked in the Foundation milestone.
