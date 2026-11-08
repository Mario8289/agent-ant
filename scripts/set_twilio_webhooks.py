"""Point the Twilio number's voice and SMS webhooks at ``PUBLIC_BASE_URL``.

A quick tunnel (``cloudflared`` with no account, free ngrok) gets a new hostname every time it
restarts. Twilio keeps calling the old one until it is told otherwise, so after a restart the
number has to be re-pointed. That is two settings on the same resource, and doing it by hand is
easy to half-finish: a voice webhook on the new host with an SMS webhook still on the dead one
looks like a working call path until someone replies.

Twilio signs the exact URL it calls, so ``PUBLIC_BASE_URL`` here must match the app's setting.
This only writes the Twilio side; it does not touch ``.env``.

Usage: ``just repoint`` (requires the tunnel running and ``PUBLIC_BASE_URL`` set).
"""

import sys

from twilio.rest import Client

from agent_ant_core.config import get_settings

VOICE_PATH = "/webhooks/missed-call"
SMS_PATH = "/webhooks/sms-reply"


def main() -> int:
    settings = get_settings()
    missing = [
        name
        for name in (
            "PUBLIC_BASE_URL",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_FROM_NUMBER",
        )
        if not getattr(settings, name.lower(), None)
    ]
    if missing:
        print(f"missing in .env: {', '.join(missing)}", file=sys.stderr)
        return 1

    # get_settings only returns here if these are set; the asserts narrow the types.
    assert settings.public_base_url is not None
    assert settings.twilio_account_sid is not None
    assert settings.twilio_auth_token is not None
    assert settings.twilio_from_number is not None

    base = settings.public_base_url.rstrip("/")
    client = Client(
        settings.twilio_account_sid,
        settings.twilio_auth_token.get_secret_value(),
    )

    numbers = client.incoming_phone_numbers.list(phone_number=settings.twilio_from_number)
    if not numbers:
        print(
            f"no Twilio number {settings.twilio_from_number} on this account; "
            "check TWILIO_FROM_NUMBER (E.164, leading +)",
            file=sys.stderr,
        )
        return 1

    for number in numbers:
        print(f"{number.phone_number}")
        print(f"  before  voice: {number.voice_method} {number.voice_url}")
        print(f"  before  sms  : {number.sms_method} {number.sms_url}")
        number.update(
            voice_url=f"{base}{VOICE_PATH}",
            voice_method="POST",
            sms_url=f"{base}{SMS_PATH}",
            sms_method="POST",
        )
        updated = client.incoming_phone_numbers(number.sid).fetch()
        print(f"  after   voice: {updated.voice_method} {updated.voice_url}")
        print(f"  after   sms  : {updated.sms_method} {updated.sms_url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
