# agent-ant

A Python-first monorepo for building AI agents and the products around them.

The first product is a **missed-call → booked-job** assistant for sole traders (Trades AI):
a missed call triggers a fixed-template text, the caller's reply is turned into a structured
job record, and the tradesperson approves or edits it.

## Where things are

| Path | What |
|---|---|
| [docs/](./docs/README.md) | **Start here.** PRD, design doc, C4 diagrams, decision records, runbooks |
| `apps/api` | The FastAPI service: Twilio webhooks, the approval dashboard, background tasks |
| `agents/missed_call` | The missed-call extraction agent (versioned prompts, LangGraph approval graph) |
| `packages/core` | Shared library: database, LLM client, audit, metrics |
| `evals/` | Golden sets and evaluation suites (`just eval`, paid) |
| `migrations/` | Alembic migrations |
| `infra/` | Local Postgres (`docker/`) and the scheduled-jobs CDK stack (`cdk/`) |
| `spikes/` | Learning exercises, not product code |

Working in the code? Read [AGENTS.md](./AGENTS.md) first. `just setup`, then `just check`.

## Status

The MVP (Weeks 1–5) is built but **not live**. Go-live waits on the deferred pre-sprint gates,
and the discovery decision ([#143](https://github.com/Mario8289/agent-ant/issues/143)) comes
first. Current state: [execution plan](./docs/planning/execution-plan.md).
