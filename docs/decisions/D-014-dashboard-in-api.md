---
id: D-014
title: "Dashboard lives in the API (one service), server-rendered"
status: accepted
date: 2026-11-09
---

# D-014 — Dashboard lives in the API (one service), server-rendered

- **Date:** 2026-11-09
- **Status:** accepted
- **Reversible?** cheap — the routes and templates can move to a separate app later.

## Context

#28 asks where the HITL dashboard lives relative to the `apps/dashboard`
placeholder. D-005 commits to one service and one Postgres, so a second deployable would break
that.

## Decision

The dashboard is routes plus Jinja2 templates inside `apps/api` — no second
service. It is server-rendered to keep the repository Python-only. The approval logic
(`approve` / `edit` / `reject`, and the `human_edits` diff) lives in `packages/core`
(`db/approval.py`); the app layer does only HTTP and templating. `apps/dashboard` stays as a
pointer, not a service.

## Consequences

One process serves both webhooks and the dashboard. A JSON API can be added
later without moving the approval logic. No SPA or build toolchain.

## Source

D-005; issue #28
