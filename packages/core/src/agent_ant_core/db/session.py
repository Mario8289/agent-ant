"""Database engine and session factory."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from agent_ant_core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Return the process-wide engine.

    ``pool_pre_ping`` avoids handing out a connection the server has already closed, which
    matters for a long-running service behind a managed Postgres.
    """
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_sessionmaker() -> sessionmaker[Session]:
    # A sessionmaker is a lightweight factory: it holds the engine and the config. Creating
    # one per request is cheap and avoids shared mutable state; the engine is the expensive
    # part and it is cached in get_engine().
    return sessionmaker(get_engine(), expire_on_commit=False)
