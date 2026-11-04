import pytest

from agent_ant_core.config import Settings, get_settings


def test_defaults_are_local_and_startable() -> None:
    settings = Settings()
    assert settings.environment == "local"
    assert settings.database_url.startswith("postgresql+psycopg://")


def test_secrets_are_not_rendered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "super-secret")
    settings = Settings()
    assert settings.twilio_auth_token is not None
    assert settings.twilio_auth_token.get_secret_value() == "super-secret"
    assert "super-secret" not in repr(settings)


def test_settings_are_cached() -> None:
    assert get_settings() is get_settings()
