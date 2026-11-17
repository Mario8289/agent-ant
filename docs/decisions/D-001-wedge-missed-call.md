---
id: D-001
title: "Wedge is missed call → auto-text → job record"
status: accepted
date: 2026-11-04
---

# D-001 — Wedge is missed call → auto-text → job record

- **Date:** 2026-11-04
- **Status:** accepted
- **Reversible?** cheap — no code exists yet.

## Context

A vertical assistant for sole traders could start anywhere (invoicing, quoting,
scheduling). The first product must be demoable quickly and avoid financial compliance.

## Decision

Start with the missed call. It is a live, frequent, monetisable loss.
Invoice-chasing is deferred until the wedge has earned trust.

## Consequences

Everything depends on carrier forwarding (R1) and on callers replying to
an SMS (H6). Both are tested before and early in the build.

## Source

[business plan](../product/business-plan.md) §1
