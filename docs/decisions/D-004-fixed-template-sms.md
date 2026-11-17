---
id: D-004
title: "Customer-facing SMS is a fixed template only"
status: accepted
date: 2026-11-04
---

# D-004 — Customer-facing SMS is a fixed template only

- **Date:** 2026-11-04
- **Status:** accepted
- **Reversible?** cheap, but revisit only with evidence from live data.

## Context

An LLM writing to customers carries reputational risk while H2 and H6 are
unproven.

## Decision

The AI never writes free text to customers. LLM output goes to Dad only.

## Consequences

Replies are less personal. Hallucination blast radius is capped.

## Source

Huyen — AI Engineering (2025); [business plan](../product/business-plan.md) §5
