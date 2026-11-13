"""End-to-end: a stored reply becomes a validated job record plus an audit row.

The background extraction task opens its own session, so the test injects both a fake provider
and a session factory bound to the throwaway test database.
"""

import json
from collections.abc import Callable, Iterator

from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator

from agent_ant_api.extraction import get_llm, get_session_factory
from agent_ant_api.main import create_app
from agent_ant_api.webhooks import get_session
from agent_ant_core.config import Settings, get_settings
from agent_ant_core.db.models import JobRecord, LLMOutputAudit
from agent_ant_core.llm import LLM
from agent_ant_core.testing import FakeLLM

TOKEN = "test_token"
CALL_PATH = "/webhooks/missed-call"
REPLY_PATH = "/webhooks/sms-reply"
CALL = {"CallSid": "CA00000000000000000000000000000001", "From": "+447000000000"}
REPLY = {
    "MessageSid": "SM00000000000000000000000000000001",
    "From": "+447000000000",
    "Body": "need a wardrobe fitted in Leeds",
}
GOOD = json.dumps(
    {"name": "Sam", "job_type": "wardrobe fitting", "location": "Leeds", "urgency": "high"}
)


def _use(session: Session) -> Callable[[], Iterator[Session]]:
    def dependency() -> Iterator[Session]:
        yield session

    return dependency


def _client(session: Session, engine: Engine, llm: LLM | None) -> TestClient:
    values: dict[str, object] = {"twilio_auth_token": SecretStr(TOKEN)}
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, **values)  # type: ignore[arg-type]
    app.dependency_overrides[get_session] = _use(session)
    app.dependency_overrides[get_llm] = lambda: llm
    app.dependency_overrides[get_session_factory] = lambda: lambda: Session(engine)
    return TestClient(app)


def _sign(url: str, form: dict[str, str]) -> dict[str, str]:
    return {"X-Twilio-Signature": RequestValidator(TOKEN).compute_signature(url, form)}


def _post(client: TestClient, path: str, form: dict[str, str]) -> None:
    url = str(client.base_url).rstrip("/") + path
    assert client.post(path, data=form, headers=_sign(url, form)).status_code == 200


def test_reply_is_extracted_into_a_job_and_audit_row(session: Session, engine: Engine) -> None:
    client = _client(session, engine, FakeLLM(GOOD))
    _post(client, CALL_PATH, CALL)
    _post(client, REPLY_PATH, REPLY)

    job = session.execute(select(JobRecord)).scalar_one()
    assert job.status == "captured"
    assert job.job_type == "wardrobe fitting"
    assert job.caller_number == "+447000000000"

    audit = session.execute(select(LLMOutputAudit)).scalar_one()
    assert audit.job_id == job.id
    assert audit.validated is True


def test_reply_is_not_extracted_when_no_provider_is_configured(
    session: Session, engine: Engine
) -> None:
    client = _client(session, engine, None)
    _post(client, CALL_PATH, CALL)
    _post(client, REPLY_PATH, REPLY)

    assert session.execute(select(JobRecord)).scalars().all() == []
    assert session.execute(select(LLMOutputAudit)).scalars().all() == []


def test_stop_reply_is_not_extracted(session: Session, engine: Engine) -> None:
    client = _client(session, engine, FakeLLM(GOOD))
    _post(client, CALL_PATH, CALL)
    _post(client, REPLY_PATH, {**REPLY, "Body": "STOP"})

    assert session.execute(select(JobRecord)).scalars().all() == []
    assert session.execute(select(LLMOutputAudit)).scalars().all() == []
