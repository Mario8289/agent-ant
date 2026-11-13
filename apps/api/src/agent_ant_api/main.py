"""FastAPI application factory and routes."""

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from agent_ant_api.dashboard import router as dashboard_router
from agent_ant_api.webhooks import router as webhooks_router
from agent_ant_core.config import get_settings
from agent_ant_core.db.session import get_sessionmaker


def create_app() -> FastAPI:
    """Build the application.

    A factory (rather than a module-level singleton) keeps tests isolated and makes it easy
    to build an app with overridden settings.
    """
    settings = get_settings()
    # Uvicorn configures its own loggers but not the root one, so without this every
    # ``logger.info`` in the app is dropped and the deployment logs say nothing about what
    # happened to a call. Honour LOG_LEVEL for both halves of the process.
    logging.basicConfig(
        level=settings.log_level,
        format="%(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("agent_ant_api").setLevel(settings.log_level)
    # The Twilio SDK logs a full request per send at INFO, including the account SID. Keep
    # library noise, and its identifiers, out of the app log.
    logging.getLogger("twilio").setLevel(logging.WARNING)

    app = FastAPI(title="agent-ant api", version="0.1.0")
    app.include_router(webhooks_router)
    app.include_router(dashboard_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    @app.get("/ready")
    def ready() -> JSONResponse:
        """Readiness probe: the process is up *and* the database answers a SELECT 1.

        App Runner points its health check here, so an instance is only "healthy" while it can
        actually serve traffic. A broken database returns 503 rather than crashing the probe.
        """
        try:
            with get_sessionmaker()() as session:
                session.execute(text("SELECT 1"))
        except Exception:
            return JSONResponse(status_code=503, content={"status": "unavailable"})
        return JSONResponse(status_code=200, content={"status": "ready"})

    return app


app = create_app()
