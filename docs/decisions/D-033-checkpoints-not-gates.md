---
id: D-033
title: "Gates become checkpoints, go-live is readiness-based, and more than one agent is allowed"
status: accepted
date: 2026-11-22
---

# D-033 — Gates become checkpoints, go-live is readiness-based, and more than one agent is allowed

- **Date:** 2026-11-22
- **Status:** accepted
- **Reversible?** cheap. It changes plans and labels, not code. The risk it accepts is in
  Consequences.

## Context

The plan so far: build one agent (D-003), go live in Week 4 (D-006), and treat discovery (G0a),
the forwarding test (G0b) and the beachhead choice (#15) as gates. D-010 let Week 1 start before
them, with a failed G0a still meaning stop.

What has changed:

- The MVP is built but not live. Dad, the design partner, will not allow live customers until the
  product is more polished.
- Interview 1 did not support H1 (a specific missed call and lost job). It did show a different
  pain: receipts in an envelope (H9). [Findings](../discovery/findings.md).
- The founder wants a mobile product that gives a sole trader the feel of a team (D-034), and
  more agents than `missed_call`, starting with receipts.
- Interviews are slow to schedule. The founder wants them to guide direction without holding up
  the build.

## Options considered

| Option | Outcome |
|---|---|
| A Keep the gates and the Week 4 date | Blocks all new work on interviews that are slow to arrive. Contradicts what Dad has said about going live |
| **B** (chosen) Interviews run alongside the build as checkpoints, and go-live waits for readiness | Work continues. Discovery still steers it. Cost: nothing forces a stop |
| C Drop discovery | Builds on one interview. Rejected: the evidence base is already thin |

## Decision

1. **G0a (#10, #143), G0b (#47) and the beachhead choice (#15) are checkpoints, not gates.**
   Interviews continue in parallel with no decision points. Findings guide direction and can
   reorder the roadmap. "A failed G0a means stop" no longer applies. The H1 pass line (at least
   3 of 6) stays in the hypotheses as a measurement.
2. **Go-live is readiness-based, with no date.** The Week 4 and Week 6 labels are retired. Dad
   has the final say. The checklist (proposed, tracked in a go-live issue):
   - trader login
   - the mobile app
   - chat with the team on WhatsApp (post-go-live, not required to go live)
   - the receipts agent working end to end
   - the forwarding test passing on Dad's own handset and plan (what G0b tests, now a technical
     check, not a strategic gate)
   - the DPA and paid LLM tier confirmed (#16, D-018)
   - Dad says it is polished enough
3. **More than one agent may be built.** D-003's "no second agent" no longer applies. Build one
   at a time, each under the same non-negotiables. First: receipts (the Bookkeeper). Clarifying
   questions for the Receptionist (D-035, Level 1) are deferred out of the MVP. Skeletons of the
   quote drafter and follow-up chaser follow, with a fake LLM in tests.
4. **D-031 is amended, not replaced.** Receipts is promoted ahead of agents 1–4. The gates it
   lists as blockers (#10, #32, #37) no longer block. The lifecycle (D-030, epic #121) remains a
   prerequisite for agents that need job states. Agents 5–12 stay as rows in the roadmap.
5. **What does not change:** the non-negotiables in `AGENTS.md`. Synthetic data only until the
   DPA is locked. Nothing reaches a real customer before go-live readiness. D-004, D-005 and the
   persist-before-processing and idempotency rules stand.

## Consequences

- **Risk accepted:** building before the missed-call wedge is validated. The product no longer
  rests on that wedge alone, and receipts has early evidence from Dad. That is one interview.
  Revisit this decision if six interviews are logged and none describes a missed call or
  paperwork pain.
- The execution plan, PRD, roadmap and `AGENTS.md` are updated in the same PR. GitHub gets a
  "Discovery (parallel)" milestone and a "Go-live" milestone, and #10, #140–#143, #47 and #15
  lose the `pre-sprint` label.
- `Closes` language on issues for the retired gates changes to "checkpoint". None is closed by
  this PR.

## Source

Founder decisions, 2026-11-22; [discovery findings](../discovery/findings.md) interview 1;
supersedes D-003, D-006, D-010; amends D-031.
