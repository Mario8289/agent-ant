"""Voicemail-to-text (issue #33): a transcript becomes a stored event and a captured job.

Twilio posts the transcript to ``/webhooks/voicemail-transcription`` asynchronously, after the
caller has hung up. The test injects a fake provider and a session factory bound to the throwaway
test database, exactly like the SMS-reply extraction tests.
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
from agent_ant_core.db.extraction import DONE
from agent_ant_core.db.models import JobRecord, LLMOutputAudit, RawEvent
from agent_ant_core.llm import LLM
from agent_ant_core.testing import FakeLLM

TOKEN = "test_token"
CALL_PATH = "/webhooks/missed-call"
VOICEMAIL_PATH = "/webhooks/voicemail-transcription"
CALL = {"CallSid": "CA00000000000000000000000000000001", "From": "+447000000000"}
VOICEMAIL = {
    "RecordingSid": "RE00000000000000000000000000000001",
    "TranscriptionSid": "TR00000000000000000000000000000001",
    "TranscriptionText": "need a wardrobe fitted in Leeds",
    "TranscriptionStatus": "completed",
    "CallSid": CALL["CallSid"],
    "From": CALL["From"],
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


def test_completed_transcription_is_stored_linked_and_extracted(
    session: Session, engine: Engine
) -> None:
    client = _client(session, engine, FakeLLM(GOOD))
    _post(client, CALL_PATH, CALL)
    _post(client, VOICEMAIL_PATH, VOICEMAIL)

    call = session.execute(select(RawEvent).where(RawEvent.source == "voice_call")).scalar_one()
    voicemail = session.execute(select(RawEvent).where(RawEvent.source == "voicemail")).scalar_one()
    assert voicemail.idempotency_key == VOICEMAIL["RecordingSid"]
    assert voicemail.caller_number == CALL["From"]
    assert voicemail.related_event_id == call.id  # linked by CallSid, not number heuristic
    assert voicemail.extraction_status == DONE
    assert voicemail.extraction_attempts == 1

    job = session.execute(select(JobRecord)).scalar_one()
    assert job.status == "captured"
    assert job.job_type == "wardrobe fitting"
    assert job.idempotency_key == VOICEMAIL["RecordingSid"]

    audit = session.execute(select(LLMOutputAudit)).scalar_one()
    assert audit.job_id == job.id
    assert audit.validated is True


def test_failed_transcription_is_stored_but_not_extracted(session: Session, engine: Engine) -> None:
    client = _client(session, engine, FakeLLM(GOOD))
    _post(client, CALL_PATH, CALL)
    _post(client, VOICEMAIL_PATH, {**VOICEMAIL, "TranscriptionStatus": "failed"})

    voicemail = session.execute(select(RawEvent).where(RawEvent.source == "voicemail")).scalar_one()
    assert voicemail.extraction_status is None  # never scheduled
    assert session.execute(select(JobRecord)).scalars().all() == []
    assert session.execute(select(LLMOutputAudit)).scalars().all() == []


def test_duplicate_recording_sid_is_stored_once(session: Session, engine: Engine) -> None:
    client = _client(session, engine, FakeLLM(GOOD))
    _post(client, CALL_PATH, CALL)
    _post(client, VOICEMAIL_PATH, VOICEMAIL)
    _post(client, VOICEMAIL_PATH, VOICEMAIL)  # at-least-once delivery

    voicemails = (
        session.execute(select(RawEvent).where(RawEvent.source == "voicemail")).scalars().all()
    )
    assert len(voicemails) == 1


def test_voicemail_without_a_missed_call_is_stored_unlinked(
    session: Session, engine: Engine
) -> None:
    client = _client(session, engine, FakeLLM(GOOD))
    # No CALL posted, and a CallSid that matches nothing.
    _post(client, VOICEMAIL_PATH, {**VOICEMAIL, "CallSid": "CA00000000000000000000000000000099"})

    voicemail = session.execute(select(RawEvent).where(RawEvent.source == "voicemail")).scalar_one()
    assert voicemail.related_event_id is None
    assert voicemail.extraction_status == DONE  # still extracted, just unlinked


def test_missing_recording_sid_is_rejected(session: Session, engine: Engine) -> None:
    client = _client(session, engine, FakeLLM(GOOD))
    url = str(client.base_url).rstrip("/") + VOICEMAIL_PATH
    form = {k: v for k, v in VOICEMAIL.items() if k != "RecordingSid"}
    assert client.post(VOICEMAIL_PATH, data=form, headers=_sign(url, form)).status_code == 400
    assert session.execute(select(RawEvent)).scalars().all() == []


def test_bad_signature_is_rejected(session: Session, engine: Engine) -> None:
    client = _client(session, engine, FakeLLM(GOOD))
    url = str(client.base_url).rstrip("/") + VOICEMAIL_PATH
    headers = _sign(url, {**VOICEMAIL, "From": "+447999999999"})  # sign a different body
    assert client.post(VOICEMAIL_PATH, data=VOICEMAIL, headers=headers).status_code == 403
    assert session.execute(select(RawEvent)).scalars().all() == []
