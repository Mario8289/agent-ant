import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine

from agent_ant_api.main import create_app
from agent_ant_core.db import session as db_session


def test_health_reports_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_reports_ready_when_database_reachable(
    engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(db_session, "get_engine", lambda: engine)
    client = TestClient(create_app())
    assert client.get("/ready").status_code == 200


def test_ready_reports_unavailable_when_database_down(monkeypatch: pytest.MonkeyPatch) -> None:
    # An unreachable Postgres fails fast (connection refused), so the probe returns 503 rather
    # than hanging or crashing the health check.
    bad = create_engine(
        "postgresql+psycopg://u:p@127.0.0.1:59999/x", connect_args={"connect_timeout": 1}
    )
    monkeypatch.setattr(db_session, "get_engine", lambda: bad)
    client = TestClient(create_app())
    assert client.get("/ready").status_code == 503
