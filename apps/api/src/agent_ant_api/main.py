"""FastAPI application factory and routes."""

from fastapi import FastAPI

from agent_ant_core.config import get_settings


def create_app() -> FastAPI:
    """Build the application.

    A factory (rather than a module-level singleton) keeps tests isolated and makes it easy
    to build an app with overridden settings.
    """
    settings = get_settings()
    app = FastAPI(title="agent-ant api", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
