"""Critical-path tests for the missed-call webhook.

Signing uses Twilio's own ``RequestValidator`` so the tests exercise the real algorithm. The
rejection tests give the app a database session that explodes, proving a rejected request never
reaches the database.
"""

import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterator

from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator

from agent_ant_api.main import create_app
from agent_ant_api.sms import (
    SmsSender,
    build_help_reply,
    build_missed_call_message,
    build_stop_confirmation,
    get_sms_sender,
)
from agent_ant_api.webhooks import get_session
from agent_ant_core.config import Settings, get_settings
from agent_ant_core.db.models import OptOut, RawEvent

TOKEN = "test_token"
PATH = "/webhooks/missed-call"
FORM = {"CallSid": "CA00000000000000000000000000000001", "From": "+447000000000"}


def _no_database() -> Iterator[Session]:
    raise AssertionError("a rejected request must not touch the database")
    yield  # pragma: no cover


def _use(session: Session) -> Callable[[], Iterator[Session]]:
    def dependency() -> Iterator[Session]:
        yield session

    return dependency


def _client(
    session_dependency: Callable[[], Iterator[Session]] = _no_database,
    sms_sender: SmsSender | None = None,
    **settings: object,
) -> TestClient:
    values: dict[str, object] = {"twilio_auth_token": SecretStr(TOKEN), **settings}
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, **values)  # type: ignore[arg-type]
    app.dependency_overrides[get_session] = session_dependency
    app.dependency_overrides[get_sms_sender] = lambda: sms_sender
    return TestClient(app)


def _sign(url: str, form: dict[str, str] = FORM) -> dict[str, str]:
    return {"X-Twilio-Signature": RequestValidator(TOKEN).compute_signature(url, form)}


def _url(client: TestClient) -> str:
    return str(client.base_url).rstrip("/") + PATH


def test_missing_signature_is_rejected() -> None:
    assert _client().post(PATH, data=FORM).status_code == 403


def test_tampered_body_is_rejected() -> None:
    client = _client()
    headers = _sign(_url(client))
    assert (
        client.post(PATH, data={**FORM, "From": "+447999999999"}, headers=headers).status_code
        == 403
    )


def test_fails_closed_without_an_auth_token() -> None:
    client = _client(twilio_auth_token=None)
    assert client.post(PATH, data=FORM, headers=_sign(_url(client))).status_code == 503


def test_valid_request_is_stored_and_answered_with_twiml(session: Session) -> None:
    client = _client(_use(session))
    response = client.post(PATH, data=FORM, headers=_sign(_url(client)))

    assert response.status_code == 200
    assert ET.fromstring(response.text).tag == "Response"
    row = session.execute(select(RawEvent)).scalar_one()
    assert (row.idempotency_key, row.source, row.caller_number, row.payload) == (
        FORM["CallSid"],
        "voice_call",
        FORM["From"],
        FORM,
    )


def test_retry_gets_the_same_200_and_is_stored_once(session: Session) -> None:
    client = _client(_use(session))
    headers = _sign(_url(client))
    first = client.post(PATH, data=FORM, headers=headers)
    retry = client.post(PATH, data=FORM, headers=headers)

    assert first.status_code == retry.status_code == 200
    assert session.execute(select(func.count()).select_from(RawEvent)).scalar_one() == 1


def test_signature_is_checked_against_the_public_base_url(session: Session) -> None:
    # Behind a tunnel Twilio signs the public URL, not the one the app sees.
    public = "https://example.ngrok.app"
    client = _client(_use(session), public_base_url=public)

    assert client.post(PATH, data=FORM, headers=_sign(public + PATH)).status_code == 200


class FakeSms:
    def __init__(self, error: Exception | None = None) -> None:
        self.sent: list[tuple[str, str]] = []
        self.error = error

    def __call__(self, to: str, body: str) -> None:
        if self.error:
            raise self.error
        self.sent.append((to, body))


def test_first_delivery_sends_one_fixed_template_text(session: Session) -> None:
    sms = FakeSms()
    client = _client(_use(session), sms, business_name="Dave's Joinery")
    client.post(PATH, data=FORM, headers=_sign(_url(client)))

    assert sms.sent == [(FORM["From"], build_missed_call_message("Dave's Joinery"))]
    assert "Dave's Joinery" in sms.sent[0][1]


def test_retry_does_not_send_a_second_text(session: Session) -> None:
    sms = FakeSms()
    client = _client(_use(session), sms)
    headers = _sign(_url(client))
    client.post(PATH, data=FORM, headers=headers)
    client.post(PATH, data=FORM, headers=headers)

    assert len(sms.sent) == 1


def test_send_failure_does_not_fail_the_webhook(session: Session) -> None:
    client = _client(_use(session), FakeSms(error=TimeoutError("twilio is down")))
    response = client.post(PATH, data=FORM, headers=_sign(_url(client)))

    assert response.status_code == 200
    assert session.execute(select(func.count()).select_from(RawEvent)).scalar_one() == 1


def test_unconfigured_twilio_still_stores_and_answers(session: Session) -> None:
    client = _client(_use(session), sms_sender=None)
    response = client.post(PATH, data=FORM, headers=_sign(_url(client)))

    assert response.status_code == 200


# --- SMS reply ----------------------------------------------------------------------------

REPLY_PATH = "/webhooks/sms-reply"
REPLY = {
    "MessageSid": "SM00000000000000000000000000000001",
    "From": FORM["From"],
    "Body": "Leaky tap",
}


def test_reply_is_stored_once_and_linked_to_the_missed_call(session: Session) -> None:
    client = _client(_use(session))
    client.post(PATH, data=FORM, headers=_sign(_url(client)))
    url = str(client.base_url).rstrip("/") + REPLY_PATH
    headers = _sign(url, REPLY)

    assert client.post(REPLY_PATH, data=REPLY, headers=headers).status_code == 200
    assert client.post(REPLY_PATH, data=REPLY, headers=headers).status_code == 200

    call = session.execute(select(RawEvent).where(RawEvent.source == "voice_call")).scalar_one()
    reply = session.execute(select(RawEvent).where(RawEvent.source == "sms_reply")).scalar_one()
    assert reply.idempotency_key == REPLY["MessageSid"]
    assert reply.related_event_id == call.id


def test_reply_with_no_missed_call_is_stored_unlinked(session: Session) -> None:
    client = _client(_use(session))
    url = str(client.base_url).rstrip("/") + REPLY_PATH
    response = client.post(REPLY_PATH, data=REPLY, headers=_sign(url, REPLY))

    assert response.status_code == 200
    assert session.execute(select(RawEvent)).scalar_one().related_event_id is None


# --- STOP / HELP (issue #72) ---------------------------------------------------------------


def _post_reply(client: TestClient, body: str) -> None:
    form = {**REPLY, "Body": body}
    url = str(client.base_url).rstrip("/") + REPLY_PATH
    assert client.post(REPLY_PATH, data=form, headers=_sign(url, form)).status_code == 200


def test_stop_records_opt_out_and_confirms(session: Session) -> None:
    sms = FakeSms()
    client = _client(_use(session), sms, business_name="Dave's Joinery")
    _post_reply(client, "STOP")

    assert session.get(OptOut, FORM["From"]) is not None
    assert sms.sent == [(FORM["From"], build_stop_confirmation("Dave's Joinery"))]


def test_help_replies_without_opting_out(session: Session) -> None:
    sms = FakeSms()
    client = _client(_use(session), sms, business_name="Dave's Joinery")
    _post_reply(client, "HELP")

    assert session.get(OptOut, FORM["From"]) is None
    assert sms.sent == [(FORM["From"], build_help_reply("Dave's Joinery"))]


def test_stop_is_not_answered_by_a_second_auto_text(session: Session) -> None:
    sms = FakeSms()
    client = _client(_use(session), sms)
    _post_reply(client, "STOP")
    _post_reply(client, "STOP")  # duplicate delivery must not confirm twice

    assert len(sms.sent) == 1


def test_stop_keyword_ignores_case_and_whitespace(session: Session) -> None:
    sms = FakeSms()
    client = _client(_use(session), sms)
    _post_reply(client, "  stop ")

    assert session.get(OptOut, FORM["From"]) is not None
    assert len(sms.sent) == 1


def test_opted_out_caller_is_not_texted_on_a_missed_call(session: Session) -> None:
    sms = FakeSms()
    client = _client(_use(session), sms)
    _post_reply(client, "STOP")

    response = client.post(PATH, data=FORM, headers=_sign(_url(client)))
    assert response.status_code == 200

    # Only the STOP confirmation went out; the missed-call text was suppressed.
    assert sms.sent == [(FORM["From"], build_stop_confirmation(None))]
    assert all(body != build_missed_call_message(None) for _, body in sms.sent)
