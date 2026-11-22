---
id: D-030
title: "MVP job lifecycle: four states, kept separate from the review status"
status: accepted
date: 2026-11-22
---

# D-030 — MVP job lifecycle: four states, kept separate from the review status

- **Date:** 2026-11-22
- **Status:** accepted
- **Reversible?** cheap. Adding a state is one migration and one edit to the transitions table.
  Existing rows stay valid.

## Context

D-030 was reserved for the customer and job lifecycle (#122, epic #121). The epic's model has
ten job statuses (`enquiry → quoted → booked → in_progress ⇄ on_hold → completed → paid`, with
three exits), customer stages, actor permissions, and triggers. Most of it exists to serve agents
that are not built.

The founder wants an MVP out and said a simpler flow is acceptable (2026-11-22). The first agents
are the Receptionist (creates leads) and the Bookkeeper (attaches spend to a job under way,
D-033). Neither needs `quoted`, `awaiting payment` or `dispute`.

`job_records.status` already exists with `captured / needs_review / approved / rejected`. That
is the **extraction review** status: did the trader check what the AI read? It is not job
progress, and `approval.py` depends on it.

## Options considered

| Option | Outcome |
|---|---|
| **A** (chosen) Four states now, add the rest when the agent that needs them arrives | Nothing to build or show that no agent uses. Growth is cheap |
| B The full ten-state flow now | States and screens with nothing to do. Several would be guesses until the Estimator and invoicing agents exist |
| C Reuse `job_records.status` for progress | An "approved" job and an "In work" job become confusable, and the approval logic breaks |
| D A configurable workflow engine, or a second industry's flow now | A new product bet. Rule of three: one industry exists |
| E An external CRM (HubSpot) | Rejected in the epic: D-005, data protection, transactional idempotency |

## Decision

1. **Job progress is its own column**, `job_status`, on the job table. `status` keeps meaning
   extraction review and is not reused. Renaming `status` to `review_status` is allowed later (#124)
   and is not required by this decision.
2. **Four states.** Stored values match the epic so later states slot in without renames.

   | Stored value | Shown as | Meaning |
   |---|---|---|
   | `enquiry` | Lead | Someone got in touch and work has not started |
   | `in_progress` | In work | Agreed and under way |
   | `completed` | Complete | Work finished |
   | `lost` | Lost | Did not go ahead (from Lead only) |

   Allowed moves: `enquiry → in_progress`, `enquiry → lost`, `in_progress → completed`.
3. **On hold is a flag**, not a state: a boolean on an `in_progress` job. The epic modelled it as
   `in_progress ⇄ on_hold`. That can return as a state if a later agent needs to react to it.
4. **A lead is a job in `enquiry`.** There is no separate leads table or tab.
5. **States and moves live as data in one module in `packages/core`**, with one `transition()`
   that checks the table and writes an append-only `job_events` row (#124). No state logic is
   scattered through routes or agents. This is the seam for other industries. It is not a workflow
   engine.
6. **MVP moves are made by the trader.** Agents create leads but do not move jobs. Actor
   permissions are not needed until an agent proposes transitions.
7. **Growth order**, each added with the agent that needs it, names settled then:
   - Quoted, between Lead and In work, with the Estimator.
   - Awaiting payment, Dispute and Closed after Complete, with the invoicing agent.
   - Booked, paid, declined and cancelled from the epic are candidates for the same work.

## Consequences

- The Jobs tab has three chips: Leads, In work, Complete. Lost sits under an archive link.
- #124 is scoped to this table and `job_events`. #125 and #126 stay out of the MVP.
- **Not decided here, and still open on #122:** customer stages (#123), actor permissions,
  transition triggers and scheduled actions (#126), and gaps G1–G4 in
  [roadmap §7](../product/roadmap.md). They are needed when agents begin proposing transitions
  or following up on a schedule, so they get their own decision then. Gap G1 (create the job when
  the call is missed, not when the caller replies) matters earliest and should be settled before
  the Receptionist's clarifying questions.
- The epic's "Model" section is superseded for the MVP by this record. Its later-state and
  permission content remains the starting point for the follow-up decision.

## Source

Founder decision, 2026-11-22; epic #121; [roadmap §7](../product/roadmap.md);
`packages/core/src/agent_ant_core/db/models.py` and `approval.py` (existing `status`); D-005.
