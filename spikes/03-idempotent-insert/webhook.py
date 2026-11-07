"""Spike 3: webhook that persists the raw event idempotently, then answers 200.

Persist-before-processing and dedupe-on-CallSid together: a Twilio retry of an already
stored call still gets a normal 200 (a 4xx/5xx would make Twilio retry again), but no
second row is written and no second job would be started.

The handler is a plain `def` so FastAPI runs it in a threadpool; psycopg is blocking.
"""

from datetime import UTC, datetime

from fastapi import FastAPI, Form, Response
from store import connect, insert_event

app = FastAPI()

TWIML = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<Response><Say>Thanks, we have your message.</Say></Response>"
)


@app.post("/webhook/voice")
def voice(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
) -> Response:
    with connect() as conn:
        inserted = insert_event(
            conn,
            idempotency_key=CallSid,
            caller_number=From,
            received_at=datetime.now(UTC),
            raw_payload={"CallSid": CallSid, "From": From, "To": To},
        )
    # Duplicate or not, answer the same: only a new event should trigger processing.
    headers = {"X-Duplicate": "false" if inserted else "true"}
    return Response(content=TWIML, media_type="application/xml", headers=headers)
