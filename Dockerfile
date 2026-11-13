# Production image for the stateless FastAPI service (D-020, #29).
#
# Single-stage on the uv image: the workspace source is copied in and installed, so the app and
# its Jinja2 templates live at their natural repo paths (the dashboard loads templates from the
# filesystem). The app is small; a multi-stage lean build is not worth the extra indirection yet.
#
# Migrations are NOT run here: they live in `migrations/` at the repo root and run from the repo
# against Supabase as a separate deploy step (see docs/10). The image only serves the app.

FROM ghcr.io/astral-sh/uv:0.13.7-python3.12-trixie-slim

WORKDIR /app

# The workspace manifest and lockfile, then the three packages the API depends on.
COPY pyproject.toml uv.lock ./
COPY packages ./packages
COPY agents ./agents
COPY apps ./apps

# Install the API and its workspace deps only; no dev group, frozen to the committed lockfile.
RUN uv sync --frozen --no-dev --package agent-ant-api

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

# Same command as `just dev`, minus --reload.
CMD ["uvicorn", "agent_ant_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "apps/api/src"]
