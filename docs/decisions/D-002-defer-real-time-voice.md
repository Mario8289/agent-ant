---
id: D-002
title: "Real-time voice deferred past Week 6"
status: accepted
date: 2026-11-04
---

# D-002 — Real-time voice deferred past Week 6

- **Date:** 2026-11-04
- **Status:** accepted
- **Reversible?** cheap

## Context

v0.1 put voice in Week 5. It was the highest-risk component (latency, cost,
complexity) and no hypothesis requires it.

## Decision

Real-time voice is out of scope. Optional async voicemail-to-text may appear
in Week 5.

## Consequences

The MVP is text-only. Coverage is lower for callers who leave no voicemail.

## Source

[business plan](../product/business-plan.md) §7, [design doc](../design/design-doc.md)
