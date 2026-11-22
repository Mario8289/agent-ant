---
id: D-003
title: "6-week goal is a one-agent prototype"
status: superseded by D-033
date: 2026-11-04
---

# D-003 — 6-week goal is a one-agent prototype

- **Date:** 2026-11-04
- **Status:** superseded by D-033
- **Reversible?** cheap

## Context

The repo is structured for several agents and products, but only one
assumption set has been defined.

## Decision

Build one agent (`missed_call`). Multi-agent orchestration, social and
procurement agents are out of scope for 6 weeks. The repo layout may have room for more,
but no second agent is built.

## Consequences

Shared code in `packages/core` is extracted only when a second consumer
exists, or when the first agent clearly needs it.

## Source

[business plan](../product/business-plan.md) §9
