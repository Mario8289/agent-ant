# Spike 03: idempotent insert (#59)

Shows that a duplicate `idempotency_key` (Twilio `CallSid`) is rejected by a Postgres unique
constraint and handled, not a crash. Synthetic data only.

| File | Purpose |
|---|---|
| `store.py` | Table with `idempotency_key UNIQUE`; `insert_event` uses `ON CONFLICT DO NOTHING` and returns `False` for a duplicate |
| `webhook.py` | Form-encoded `/webhook/voice` that stores the raw event, returns 200 on retries too |
| `test_idempotent_insert.py` | Constraint, duplicate handling, concurrent duplicates, webhook retry |
| `docker-compose.yml` | Throwaway Postgres on port **5433** |

## Run the tests

From the repo root:

```bash
# 1. start Postgres (waits until healthy)
docker compose -f spikes/03-idempotent-insert/docker-compose.yml up -d --wait

# 2. run the tests against it (defaults to localhost:5433, the compose file's port)
cd spikes/03-idempotent-insert
uv run --all-packages pytest -v

# 3. clean up (removes the container and its data)
cd ../..
docker compose -f spikes/03-idempotent-insert/docker-compose.yml down
```

Expected: `6 passed`.

## "6 skipped" means Postgres was not reached

If the database is unreachable the tests **skip**, they do not pass or fail. Check the summary
line. The skip reason names the host and port that was tried.

Without `DATABASE_URL` set, the spike connects to `localhost:5433`, the compose file's
Postgres. Set `DATABASE_URL` only to point it somewhere else, e.g. the repo's main Postgres
(`just db-up`, port 5432).

## What the tests touch

They create and `TRUNCATE` one table, `spike03_inbound_events`, in whichever database
`DATABASE_URL` points at. Nothing else is changed. Use the throwaway container rather than a
database you care about.
