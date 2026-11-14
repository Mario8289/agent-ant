# agent-ant — developer commands. Run `just` to list them.

default:
    @just --list

# Install/refresh the virtualenv and lockfile
setup:
    uv sync --all-packages

# Lint and format-check
lint:
    uv run --all-packages ruff check .
    uv run --all-packages ruff format --check .

# Auto-fix lint and formatting
fmt:
    uv run --all-packages ruff check --fix .
    uv run --all-packages ruff format .

# Static types (strict on packages/core)
typecheck:
    uv run --all-packages pyright

# Unit tests only — no paid or non-deterministic evals
test:
    uv run --all-packages pytest -m "not eval"

# Evaluation suite (slow, may cost money); extra args are passed to pytest
eval *args:
    uv run --all-packages pytest evals -m eval {{args}}

# Run the API locally
dev:
    uv run --package agent-ant-api uvicorn agent_ant_api.main:app --reload --app-dir apps/api/src

# Point both Twilio webhooks at PUBLIC_BASE_URL (run after the tunnel URL changes)
repoint:
    uv run --all-packages python scripts/set_twilio_webhooks.py

# Check Bedrock credentials and the configured LLM_MODEL (needs AWS credentials)
check-llm:
    uv run --all-packages python scripts/check_llm.py

# Re-attempt failed SMS sends and dead-letter those that exhaust their retries
retry-sms:
    uv run --all-packages python scripts/retry_sms.py

# Re-run extraction over retryable replies and dead-letter the exhausted
retry-extractions:
    uv run --all-packages python scripts/retry_extractions.py

# Redact personal fields past their retention window (30d outbound, 90d raw/audit)
purge:
    uv run --all-packages python scripts/purge_old_data.py

# Erase one caller's personal data on request (D-027); e.g. `just erase +447000000000`
erase number:
    uv run --all-packages python scripts/erase_person.py {{number}}

# Send one test alert to the configured Slack webhook (issue #94)
test-slack:
    uv run --all-packages python scripts/test_slack.py

# Synth / diff / deploy the ops scheduler CDK stack (issue #96). Pass the account-specific
# values through as -c key=value; see infra/cdk/README.md for the keys. Needs Node (npx).
cdk-synth *args:
    cd infra/cdk && npx --yes aws-cdk@latest synth {{args}}

cdk-diff *args:
    cd infra/cdk && npx --yes aws-cdk@latest diff {{args}}

cdk-deploy *args:
    cd infra/cdk && npx --yes aws-cdk@latest deploy {{args}}

cdk-destroy *args:
    cd infra/cdk && npx --yes aws-cdk@latest destroy {{args}}

# Everything CI runs
check: lint typecheck test

# Local Postgres
db-up:
    docker compose -f infra/docker/docker-compose.yml up -d

# Apply database migrations (uses DATABASE_URL)
migrate:
    uv run --all-packages alembic upgrade head

db-down:
    docker compose -f infra/docker/docker-compose.yml down

db-logs:
    docker compose -f infra/docker/docker-compose.yml logs -f postgres
