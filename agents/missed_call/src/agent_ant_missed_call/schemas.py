"""Job record schema.

Mirrors ``docs/05-architecture-and-schema.md``. Two field groups are kept apart on purpose:

* **Trusted** fields come from the telephony provider and are never produced by the LLM.
* **Extracted** fields are LLM-produced, validated, and human-correctable.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

JobStatus = Literal["captured", "needs_review", "approved", "rejected"]
Urgency = Literal["low", "medium", "high", "unknown"]


class JobRecord(BaseModel):
    """A job captured from a missed call."""

    # Idempotency: providers retry webhooks, so dedupe on their message identifier.
    idempotency_key: str = Field(..., min_length=1, description="Twilio CallSid or MessageSid")

    # Trusted: from provider metadata, never extracted.
    caller_number: str = Field(..., min_length=1)
    received_at: datetime

    # Extracted: LLM-produced, validated, human-correctable.
    name: str | None = None
    job_type: str | None = None
    location: str | None = None
    urgency: Urgency = "unknown"
    preferred_date: str | None = None

    # Human-in-the-loop: nothing is customer-confirmed without approval.
    status: JobStatus = "captured"
    raw_message: str
    extraction_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime
    updated_at: datetime
