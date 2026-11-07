"""SQLAlchemy models.

``raw_events`` is the first table: the untouched inbound webhook, stored before anything else
happens to it (AGENTS.md rule 2). Everything downstream (SMS, extraction, job records) can be
replayed from here if processing fails.
"""

from datetime import datetime
from typing import Literal

from sqlalchemy import BigInteger, CheckConstraint, DateTime, MetaData, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Explicit constraint names keep Alembic revisions deterministic across machines.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

EventSource = Literal["voice_call", "sms_reply"]


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class RawEvent(Base):
    """One inbound provider event, exactly as received.

    ``idempotency_key`` is the provider's own identifier (``CallSid`` for a call,
    ``MessageSid`` for an SMS). Twilio delivers at least once, so duplicates are normal; the
    unique constraint is what makes handling them safe even when two retries arrive together.

    ``caller_number`` and ``received_at`` are trusted fields from provider metadata and the
    server clock. They are never taken from LLM output (rule 4). Twilio sends no timestamp on
    these webhooks, so ``received_at`` is when this service received the request.
    """

    __tablename__ = "raw_events"
    __table_args__ = (
        CheckConstraint("source IN ('voice_call', 'sms_reply')", name="source_valid"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    idempotency_key: Mapped[str] = mapped_column(Text, unique=True)
    source: Mapped[str] = mapped_column(Text)
    caller_number: Mapped[str] = mapped_column(Text)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, str]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
