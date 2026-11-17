---
id: D-031
title: "Agent roadmap is planned, not built: epics for agents 1–4 blocked by the prototype and its gates"
status: accepted
date: 2026-11-14
---

# D-031 — Agent roadmap is planned, not built: epics for agents 1–4 blocked by the prototype and its gates

- **Date:** 2026-11-14
- **Status:** accepted
- **Reversible?** cheap — close the issues and mark the doc superseded.

## Context

The missed-call agent is nearly complete and the founder wants the follow-on
agents ranked and written up, so the product can grow towards "a sole trader with the back
office of a larger firm". D-003 says no second agent is built during the 6 weeks, H4 (pull for
adjacent jobs) is untested, and the discovery sheet (the discovery findings) is still empty.
D-030 is reserved for the customer and job lifecycle decision (#122, ADR 0003), which is
recorded separately; this entry was renumbered to avoid the clash.

## Decision

- [agent roadmap](../product/roadmap.md) records 12 candidate agents in ranked order,
  grouped into roles (secretary, estimator, accounts clerk and so on).
- Epics and stories are written on GitHub for the first four only: quote drafter, follow-up
  chaser, booking and diary, invoice and payment chaser. Agents 5–12 stay as rows in the doc.
- Every one of those issues carries `blocked-by-gate` and is blocked by the prototype epic
  (#3), G0a (#10), the Week 4 gate (#32) and the Week 6 review (#37). The quote drafter is also
  blocked by the 10x-axis decision (#15).
- The shared customer and job lifecycle (epic #121) is a prerequisite for all four: it supplies
  the job states, the scheduled actions and the consent finding these epics rely on.
- **D-003 stays in force.** Planning is allowed; build hours on any of these agents are not.
- "Quotes priced the way the trader prices" is recorded as the candidate 10x axis for H5. It
  is a hypothesis, not a result.

## Consequences

- The Week 6 review (#37) has a concrete candidate list to accept, reorder or bin, instead of
  starting from a blank page.
- The ranking is a desk judgement. If Dad asks for something else unprompted (H4), or G0a
  fails, the epics are reordered or closed as Won't Do.
- How D-004 applies to quotes is an open question in the agent roadmap and needs its own decision before
  the quote drafter's send story starts.

## Source

Founder decision 2026-11-14; competitor review in the agent roadmap §1; D-003, D-004.
