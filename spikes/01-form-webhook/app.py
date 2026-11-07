"""#52 Spike 1: accept a form-encoded Twilio voice webhook and answer with TwiML.

Twilio posts call webhooks as application/x-www-form-urlencoded, not JSON. FastAPI
reads those fields through Form(...), so the handler gets plain strings it can check.
"""

from fastapi import FastAPI, Form, Response

app = FastAPI()


@app.post("/webhook/voice")
async def voice(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
) -> Response:
    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response><Say>Thanks, we have your message.</Say></Response>"
    )
    return Response(content=twiml, media_type="application/xml")
