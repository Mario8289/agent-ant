"""Business metrics for the missed-call funnel (issue #30).

The four numbers the founder actually acts on (docs/01 "Metric definitions"): capture rate,
reply rate, jobs booked and edit rate. Each is computed as a ratio over the persisted tables so
it is a measurement, not a guess, and the raw counts are carried alongside the rates so the
dashboard can show "3 / 10" rather than a bare percentage. Definitions are frozen in D-022.
"""

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agent_ant_core.db.models import (
    HumanEdit,
    JobRecord,
    LLMOutputAudit,
    OutboundMessage,
    RawEvent,
)


@dataclass(frozen=True)
class Metrics:
    """Counts and the rates derived from them. Rates are 0 when the denominator is empty.

    ``sms_jobs`` and ``voicemail_jobs`` are an additive breakdown of ``jobs`` by capture path
    (#33), shown on the dashboard. They are not part of the frozen D-022 definitions, and they
    always sum to ``jobs`` (a job's raw event is an SMS reply or a voicemail, never a call).
    """

    missed_calls: int
    jobs: int
    texts_sent: int
    replies: int
    jobs_booked: int
    edited_jobs: int
    sms_jobs: int
    voicemail_jobs: int

    @property
    def capture_rate(self) -> float:
        """Jobs captured per missed call: ``jobs / missed_calls``."""
        return self.jobs / self.missed_calls if self.missed_calls else 0.0

    @property
    def reply_rate(self) -> float:
        """Replies per auto-text sent: ``replies / texts_sent`` (gates H6)."""
        return self.replies / self.texts_sent if self.texts_sent else 0.0

    @property
    def edit_rate(self) -> float:
        """Human-edited jobs per AI job: ``edited_jobs / jobs`` (LLM drift alarm)."""
        return self.edited_jobs / self.jobs if self.jobs else 0.0


def compute_metrics(session: Session) -> Metrics:
    """Count the funnel from the persisted tables and return the metrics.

    ``jobs`` counts every ``job_records`` row — a job is "captured" the moment extraction writes
    it, whatever its later status. ``edited_jobs`` counts distinct jobs with at least one
    ``human_edits`` row. ``texts_sent`` counts ``outbound_messages`` (D-021), which is what makes
    the reply-rate denominator real rather than "missed calls".
    """
    missed_calls = session.scalar(
        select(func.count()).select_from(RawEvent).where(RawEvent.source == "voice_call")
    )
    jobs = session.scalar(select(func.count()).select_from(JobRecord))
    texts_sent = session.scalar(select(func.count()).select_from(OutboundMessage))
    replies = session.scalar(
        select(func.count()).select_from(RawEvent).where(RawEvent.source == "sms_reply")
    )
    jobs_booked = session.scalar(
        select(func.count()).select_from(JobRecord).where(JobRecord.status == "approved")
    )
    edited_jobs = session.scalar(
        select(func.count(func.distinct(JobRecord.id)))
        .select_from(HumanEdit)
        .join(LLMOutputAudit, HumanEdit.llm_output_id == LLMOutputAudit.id)
        .join(JobRecord, LLMOutputAudit.job_id == JobRecord.id)
    )
    # Additive breakdown of jobs by capture path (#33). A job's raw event is always an sms_reply
    # or a voicemail (voice calls are never extracted), so the two sum to ``jobs``.
    jobs_by_source = dict(
        session.execute(
            select(RawEvent.source, func.count())
            .select_from(JobRecord)
            .join(RawEvent, JobRecord.raw_event_id == RawEvent.id)
            .group_by(RawEvent.source)
        ).all()
    )

    return Metrics(
        missed_calls=missed_calls or 0,
        jobs=jobs or 0,
        texts_sent=texts_sent or 0,
        replies=replies or 0,
        jobs_booked=jobs_booked or 0,
        edited_jobs=edited_jobs or 0,
        sms_jobs=jobs_by_source.get("sms_reply", 0),
        voicemail_jobs=jobs_by_source.get("voicemail", 0),
    )
