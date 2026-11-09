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
