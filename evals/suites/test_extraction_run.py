"""The real scored run: extraction against the golden set (issues #26, #27).

Skips when no provider is configured — the Bedrock adapter is gated on the manual checklist in
``docs/10``. Once a provider is in place, ``just eval`` runs this and writes a report to
``evals/reports/``, failing if the frozen threshold is not met.
"""

import pytest

from agent_ant_core.config import get_settings
from agent_ant_core.llm import build_llm
from evals.suites.scoring import load_golden_set, run_eval, write_report

pytestmark = pytest.mark.eval


def test_extraction_meets_the_frozen_threshold() -> None:
    llm = build_llm(get_settings())
    if llm is None:
        pytest.skip("no LLM provider configured; set up Bedrock per docs/10")

    report = run_eval(llm, load_golden_set())
    write_report(report)
    assert report.passes, report.field_accuracy
