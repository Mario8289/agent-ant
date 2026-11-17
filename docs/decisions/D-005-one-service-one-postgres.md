---
id: D-005
title: "One service, one Postgres, no broker"
status: accepted
date: 2026-11-04
---

# D-005 — One service, one Postgres, no broker

- **Date:** 2026-11-04
- **Status:** accepted
- **Reversible?** costly once real traffic and data exist.

## Context

A solo founder at ~2 hrs/day cannot operate distributed infrastructure.

## Decision

One FastAPI service, one Postgres (Supabase), FastAPI background tasks. No
Kafka, no queue broker, no microservices.

## Consequences

Durability relies on persisting the raw event first. A crash mid-task is
recovered by reprocessing stored events.

## Source

Kleppmann & Riccomini — DDIA, 2nd ed. (2026); [design doc](../design/design-doc.md)
