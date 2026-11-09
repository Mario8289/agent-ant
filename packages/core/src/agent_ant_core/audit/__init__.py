"""Audit trail for LLM output and human corrections (R6).

Two tables back the audit: ``llm_output_audits`` (one row per extraction, immutable) and
``human_edits`` (one row per correction, linked to the extraction). The recording helpers live
in ``records.py``; the tables are defined in ``db/models.py`` and migrated in
``migrations/versions/...0003...`` (issue #24).
"""

from agent_ant_core.audit.records import EditDiff, record_human_edit, record_llm_output

__all__ = ["EditDiff", "record_human_edit", "record_llm_output"]
