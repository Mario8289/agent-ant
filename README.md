# agent-ant

A Python-first monorepo for building AI agents and the products around them.

The first product is a **missed-call → booked-job** assistant for sole traders (Trades AI):
a missed call triggers a fixed-template text, the caller's reply is turned into a structured
job record, and the tradesperson approves or edits it.

## Where things are

| Path | What |
|---|---|
| [docs/](./docs/README.md) | Business plan, hypotheses, architecture, decision log |
| `apps/` | Deployable services (planned) |
| `agents/` | One package per agent (planned) |
| `packages/` | Shared libraries (planned) |
| `evals/` | Golden sets and evaluation suites (planned) |

## Status

Pre-build. Work is tracked in the [epic](https://github.com/Mario8289/agent-ant/issues/3)
and the milestones on GitHub. Foundation work (repo scaffold, tooling, CI) is allowed now.
Product build hours wait until the pre-sprint gates G0a and G0b pass; see
[docs/00-business-plan.md](./docs/00-business-plan.md) §6.
