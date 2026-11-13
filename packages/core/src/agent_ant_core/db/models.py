"""SQLAlchemy models.

``raw_events`` is the first table: the untouched inbound webhook, stored before anything else
happens to it (AGENTS.md rule 2). Everything downstream (SMS, extraction, job records) can be
replayed from here if processing fails.
"""

from datetime import datetime
from typing import Literal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Explicit constraint names keep Alembic revisions deterministic across machines.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",  # index
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # unique constraint
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # check constraint
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # foreign key
    "pk": "pk_%(table_name)s",  # primary key
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
    # Mapped[T] is the Python type pyright sees (T | None also sets nullable); mapped_column() is the
    # SQL type. Nothing cross-checks the two, so keep them consistent by hand.
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    idempotency_key: Mapped[str] = mapped_column(Text, unique=True)
    source: Mapped[str] = mapped_column(Text)
    caller_number: Mapped[str] = mapped_column(Text)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, str]] = mapped_column(JSONB)
    # An SMS reply points at the missed call it answers. Null for voice calls and unmatched replies.
    related_event_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("raw_events.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JobRecord(Base):
    """A job captured from a caller's reply (the ``job_records`` table).

    Mirrors the Pydantic ``JobRecord`` contract in ``agent_ant_missed_call.schemas``: trusted
    fields (``idempotency_key``, ``caller_number``, ``received_at``) come from provider metadata,
    never the LLM; everything else is extracted and human-correctable. One row per reply:
    ``idempotency_key`` is the reply's ``MessageSid`` and is unique, so a retried extraction
    cannot create a second job.
    """

    __tablename__ = "job_records"
    __table_args__ = (
        CheckConstraint(
            "status IN ('captured', 'needs_review', 'approved', 'rejected')", name="status_valid"
        ),
        CheckConstraint("urgency IN ('low', 'medium', 'high', 'unknown')", name="urgency_valid"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # The reply this job was extracted from. Anchors the job to real, persisted data.
    raw_event_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("raw_events.id"))
    idempotency_key: Mapped[str] = mapped_column(Text, unique=True)
    caller_number: Mapped[str] = mapped_column(Text)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    raw_message: Mapped[str] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    urgency: Mapped[str] = mapped_column(Text, default="unknown")
    preferred_date: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, default="captured")
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LLMOutputAudit(Base):
    """One extraction attempt, logged verbatim for drift monitoring (R6).

    Written on every extraction, valid or not, so a silent quality drop shows up as a change in
    the validated rate or the edit rate rather than a surprise. ``raw_output`` is the model's
    text (JSON when the model returned structured output), stored as-is, including malformed
    output that failed validation.

    ``raw_event_id`` anchors the row to the inbound event it ran over. ``job_id`` points at the
    ``job_records`` row it produced; it is null when extraction failed and no job was written.
    """

    __tablename__ = "llm_output_audits"
    __table_args__ = (CheckConstraint("repair_attempts >= 0", name="repair_attempts_nonnegative"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    raw_event_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("raw_events.id"))
    job_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("job_records.id"), nullable=True
    )
    model: Mapped[str] = mapped_column(Text)
    prompt_version: Mapped[str] = mapped_column(Text)
    raw_output: Mapped[str] = mapped_column(Text)
    validated: Mapped[bool] = mapped_column(Boolean)
    repair_attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class HumanEdit(Base):
    """One human correction to an extraction, for edit-rate monitoring (R6).

    ``edit_diff`` records only the fields that changed, as ``field -> {"before": ..., "after":
    ...}``. A row existing here is what makes an output count as human-edited. The sketch in
    doc 05 folds ``human_edited``/``edit_diff`` onto the audit row; a separate table keeps one
    extraction immutable and lets a single output be corrected more than once.
    """

    __tablename__ = "human_edits"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    llm_output_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("llm_output_audits.id"))
    edit_diff: Mapped[dict[str, dict[str, str | None]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OptOut(Base):
    """A caller who texted STOP and must not receive further auto-texts (#72).

    Keyed on ``caller_number`` (the ``From`` Twilio sends), so a second STOP is an idempotent
    no-op rather than a duplicate row. The number is a trusted provider field, never LLM output.
    """

    __tablename__ = "opt_outs"

    caller_number: Mapped[str] = mapped_column(Text, primary_key=True)
    opted_out_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
