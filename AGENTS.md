# AGENTS.md

Instructions for coding agents (and humans) working in this repository. Read this before
changing code. It encodes decisions recorded in `docs/06-decision-log.md`; if a rule here
conflicts with the docs, the docs win — and update this file.

## What this project is

A Python-first monorepo for building AI agents and the products around them. The first
product is a **missed-call → booked-job** assistant for sole traders. The only agent is
`missed_call`.

**Read first:** `docs/00-business-plan.md` (why), `docs/05-architecture-and-schema.md`
(how), `docs/06-decision-log.md` (what was decided).

## Non-negotiable rules

These are safety and trust rules, not style preferences.

1. **The AI never writes free-text messages to customers.** Customer-facing SMS uses a fixed
   template only. LLM output goes to the tradesperson (D-004).
2. **Persist before processing.** Store the raw inbound event before doing anything else with
   it, and return a fast 200 to the provider.
3. **Webhooks are idempotent.** Dedupe on the provider's identifier (`CallSid`, `MessageSid`)
   with a database unique constraint. At-least-once delivery means duplicates are normal.
4. **Trusted fields never come from the LLM.** `caller_number` and timestamps come from
   provider metadata.
5. **No real customer data in development.** Synthetic data only. Free LLM tiers may train on
   data; a paid tier with a UK/EU DPA is required before live traffic (R4).
6. **Human approval is required** before a job is considered confirmed.
7. **Never commit secrets.** Use `.env` (gitignored); document new variables in
   `.env.example`.

## Repository layout

```
apps/          deployable services      apps/api (agent_ant_api)
agents/        one package per agent    agents/missed_call (agent_ant_missed_call)
packages/      shared libraries         packages/core (agent_ant_core)
evals/         golden sets + suites     never run in the default test path
migrations/    Alembic
infra/docker/  local Postgres
docs/          business + architecture docs, ADRs in docs/adr/
```

**Dependency direction:** `apps` → `agents` → `packages/core`. Never the reverse. `core` must
not import from `apps` or `agents`.

## Commands

```bash
just setup       # uv sync --all-packages
just lint        # ruff check + format check
just fmt         # auto-fix
just typecheck   # pyright (strict on packages/core)
just test        # unit tests only (eval marker excluded)
just eval        # slow/paid evals
just dev         # run the API on :8000
just db-up       # local Postgres via docker compose
```

Use `uv` for everything. Add dependencies to the relevant package's `pyproject.toml`, then run
`just setup` to update `uv.lock`. Commit the lockfile.

## Conventions

- Python 3.12, type hints everywhere. `core` is type-checked strictly.
- Public functions and modules get docstrings explaining *why*, not just *what*.
- Prompts are versioned files (`prompts/<name>_v<n>.md`), never inline strings. Bump the
  version when output can change and record it in the audit row.
- Pydantic models are the contract at every boundary (webhook payloads, LLM output, records).
- Tests: `pytest`. Put slow or paid tests behind the `eval` marker.
- Comments should explain intent. Avoid noise like `# increment counter`.

## What not to build yet

Out of scope until the docs change: real-time voice, multi-agent orchestration, microservices,
message brokers, invoicing/payments, a polished UI. The MVP is one service, one Postgres, and
background tasks (D-005).

Also: no product build work before the pre-sprint gates pass (`docs/00-business-plan.md` §6).

## When you finish a change

- `just check` passes.
- Docs updated if behaviour or decisions changed; new decisions get an entry in
  `docs/06-decision-log.md`.
- The PR body says `Closes #<n>` for each issue it resolves.
- Each closed issue gets a resolution comment linking the PR and the files it delivered.
  `Closes #<n>` closes silently and leaves no evidence on the issue.
