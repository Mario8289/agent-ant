"""Spike 2: verify Twilio's X-Twilio-Signature before answering.

Unlike spike 01, this handler reads the *raw* form fields rather than a fixed
list of declared parameters. The signature is computed over all POST parameters,
so validating against only the fields we happen to declare would reject genuine
requests (and Twilio adds parameters without notice).
"""

import os

from fastapi import FastAPI, Request, Response

from signature import validate_signature

# Synthetic default so the spike runs with no real credentials. The product
# (#18) reads this from config/secret store, never a hard-coded token.
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "test_token")

app = FastAPI()


@app.post("/webhook/voice")
async def voice(request: Request) -> Response:
    signature = request.headers.get("X-Twilio-Signature", "")
    params = {key: str(value) for key, value in (await request.form()).items()}

    if not validate_signature(str(request.url), params, signature, AUTH_TOKEN):
        return Response(status_code=403)

    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response><Say>Thanks, we have your message.</Say></Response>"
    )
    return Response(content=twiml, media_type="application/xml")
