"""Support alerting to Slack (issue #94): the notifier posts and degrades safely."""

import json
import urllib.error
import urllib.request
from typing import cast

from pydantic import SecretStr

from agent_ant_api import notify
from agent_ant_api.notify import make_notifier, notify_support, post_to_slack


def test_post_to_slack_posts_json(monkeypatch) -> None:
    calls: list[tuple[urllib.request.Request, object]] = []

    class _Response:
        def __enter__(self) -> "_Response":
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    def fake_urlopen(request: urllib.request.Request, timeout: object | None = None) -> _Response:
        calls.append((request, timeout))
        return _Response()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    post_to_slack("https://example.com/slack-webhook", "hello")

    assert len(calls) == 1
    request, timeout = calls[0]
    assert request.full_url == "https://example.com/slack-webhook"
    assert request.get_method() == "POST"
    assert json.loads(cast(bytes, request.data)) == {"text": "hello"}
    assert timeout == notify.SLACK_TIMEOUT_SECONDS


def test_post_to_slack_swallows_errors(monkeypatch) -> None:
    def boom(request: urllib.request.Request, timeout: object | None = None) -> None:
        raise OSError("slack down")

    monkeypatch.setattr(urllib.request, "urlopen", boom)

    post_to_slack("https://example.com/slack-webhook", "hello")  # must not raise


def test_post_to_slack_surfaces_http_error_body(monkeypatch) -> None:
    import io
    from email.message import Message

    def http_error(request: urllib.request.Request, timeout: object | None = None) -> None:
        raise urllib.error.HTTPError(
            "https://example.com/slack-webhook",
            403,
            "Forbidden",
            Message(),
            io.BytesIO(b"invalid_token"),
        )

    monkeypatch.setattr(urllib.request, "urlopen", http_error)

    post_to_slack("https://example.com/slack-webhook", "hello")  # must not raise


def test_make_notifier_is_noop_when_unset() -> None:
    make_notifier(None)("ignored")  # must not raise


def test_make_notifier_posts_when_set(monkeypatch) -> None:
    captured: list[tuple[str, str]] = []
    monkeypatch.setattr(notify, "post_to_slack", lambda url, text: captured.append((url, text)))

    make_notifier("https://example.com/slack-webhook")("hi")

    assert captured == [("https://example.com/slack-webhook", "hi")]


def test_notify_support_is_noop_when_unconfigured(monkeypatch) -> None:
    class _Settings:
        slack_webhook_url = None

    monkeypatch.setattr(notify, "get_settings", lambda: _Settings())
    captured: list[str] = []
    monkeypatch.setattr(notify, "post_to_slack", lambda url, text: captured.append(text))

    notify_support("hello")

    assert captured == []


def test_notify_support_posts_when_configured(monkeypatch) -> None:
    class _Settings:
        slack_webhook_url = SecretStr("https://example.com/slack-webhook")

    monkeypatch.setattr(notify, "get_settings", lambda: _Settings())
    captured: list[tuple[str, str]] = []
    monkeypatch.setattr(notify, "post_to_slack", lambda url, text: captured.append((url, text)))

    notify_support("hello")

    assert captured == [("https://example.com/slack-webhook", "hello")]
