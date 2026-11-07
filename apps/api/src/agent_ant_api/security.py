"""Twilio webhook authentication.

Anyone who finds the webhook URL can POST to it, and every accepted POST becomes a job and,
later, a text message. The ``X-Twilio-Signature`` header proves the request came from Twilio.
This uses Twilio's own ``RequestValidator`` rather than a hand-rolled HMAC: Twilio warns
against custom implementations, and the validator handles details such as repeated parameters
and URL port variants.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request
from twilio.request_validator import RequestValidator

from agent_ant_core.config import Settings, get_settings


def signing_url(request: Request, settings: Settings) -> str:
    """The URL Twilio signed: the public base plus the path and query it requested."""
    if not settings.public_base_url:
        return str(request.url)
    url = settings.public_base_url.rstrip("/") + request.url.path
    if request.url.query:
        url += "?" + request.url.query
    return url


async def verified_twilio_form(
    request: Request, settings: Annotated[Settings, Depends(get_settings)]
) -> dict[str, str]:
    """Return the form fields, but only if the Twilio signature is valid.

    Fails closed: with no auth token configured, every request is refused (503) rather than
    accepted unverified. A missing or wrong signature is a 403.
    """
    if settings.twilio_auth_token is None:
        raise HTTPException(status_code=503, detail="Twilio auth token is not configured")

    form = await request.form()
    signature = request.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(settings.twilio_auth_token.get_secret_value())
    if not validator.validate(signing_url(request, settings), form, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    return {key: str(value) for key, value in form.items()}
