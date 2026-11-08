"""FastAPI application factory and routes."""

import logging

from fastapi import FastAPI

from agent_ant_api.webhooks import router as webhooks_router
from agent_ant_core.config import get_settings


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

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
