# Dashboard

The human-in-the-loop UI: Dad reviews, edits, approves or rejects captured job records.

Built in Week 4 (issue #28). Per D-014, the dashboard lives **inside `apps/api`** (routes +
Jinja2 templates) rather than as a separate deployable, to keep one service and one Postgres
(D-005). This directory is a pointer, not a package.

- Routes: `apps/api/src/agent_ant_api/dashboard.py`
- Template: `apps/api/src/agent_ant_api/templates/dashboard.html`
- Approval logic: `packages/core/src/agent_ant_core/db/approval.py`

See `docs/05-architecture-and-schema.md`.
