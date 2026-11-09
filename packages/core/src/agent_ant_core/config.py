"""Application settings, loaded from the environment (and ``.env`` if present)."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Settings is the app's single, typed view of its configuration.
# Everything the app needs from outside — the database URL,
# Twilio credentials, the business name, the public URL — is read
# there, once, and turned into a validated Python object.


class Settings(BaseSettings):
    """Runtime configuration.

    Every value has a safe default so the app starts locally without a ``.env``.
    Secrets are ``SecretStr`` so they cannot leak into logs by accident.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["local", "test", "staging", "production"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Database
    database_url: str = "postgresql+psycopg://agent_ant:agent_ant@localhost:5432/agent_ant"

    # Twilio (populated in Week 1)
    twilio_account_sid: str | None = None
    twilio_auth_token: SecretStr | None = None
    twilio_from_number: str | None = None
    # Named in the auto-SMS so the text does not come from an unknown number (R2, D-011).
    business_name: str | None = None
    # Twilio signs the exact URL it called. Behind a proxy or tunnel (ngrok) the URL this app
    # sees differs from the public one, so set the public base, e.g. https://abc.ngrok.app
    public_base_url: str | None = None

    # LLM (populated in Week 2)
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_api_key: SecretStr | None = None
    # Bedrock authenticates through the AWS credential chain, not an API key. The profile is a
    # setting because pydantic-settings reads .env without exporting it to os.environ, and boto3
    # only looks at the environment; passing the name here makes AWS_PROFILE in .env work.
    aws_region: str = "eu-west-2"
    aws_profile: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""
    return Settings()
