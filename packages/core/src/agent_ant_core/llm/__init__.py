"""LLM access: structured output, validation and bounded repair (issues #22, #23).

The seam is ``LLM`` (one method: ``complete``); the extraction loop is ``extract_job``. Nothing
in this package may send free-text messages to customers; LLM output goes to the tradesperson
only (``AGENTS.md`` and decision D-004).
"""

from agent_ant_core.llm.client import LLM
from agent_ant_core.llm.extraction import (
    DEFAULT_MAX_REPAIRS,
    ExtractionResult,
    JobExtraction,
    extract_job,
    strip_code_fence,
)

__all__ = [
    "DEFAULT_MAX_REPAIRS",
    "LLM",
    "ExtractionResult",
    "JobExtraction",
    "extract_job",
    "strip_code_fence",
]
