"""The real scored runs: extraction against the golden sets (issues #26, #27).

Both skip when no provider is configured (``LLM_PROVIDER`` / ``LLM_MODEL``; setup in
``docs/10``). ``just eval`` runs them and writes reports to ``evals/reports/``.

- ``golden_v2`` is the gate (H8a, D-017): a held-out set, the mean of three runs. Only counts are
  printed, never per-message answers, so nobody tunes the prompt against it by accident.
- ``golden_v1`` is the regression guard. The prompt was tuned on it, so passing proves nothing
  new, but failing means a prompt change broke something that used to work.
"""

import pytest

from agent_ant_core.config import get_settings
from agent_ant_core.llm import build_llm
from agent_ant_missed_call.prompts import EXTRACT_PROMPT_VERSION
from evals.suites.scoring import (
    DATASET_V2,
    GATE_RUNS,
    JOB_TYPE_EXTRA_WORDS,
    format_comparison,
    format_gate_summary,
    load_golden_set,
    run_eval,
    run_gate,
    write_gate_report,
    write_report,
)

pytestmark = pytest.mark.eval


def test_gate_on_the_held_out_set() -> None:
    settings = get_settings()
    llm = build_llm(settings)
    if llm is None:
        pytest.skip("no LLM provider configured; set up Bedrock per docs/10")

    examples = load_golden_set(DATASET_V2)
    gate = run_gate(llm, examples)
    write_gate_report(
        gate,
        {
            "dataset": DATASET_V2.name,
            "messages": len(examples),
            "gate_runs": GATE_RUNS,
            "prompt_version": EXTRACT_PROMPT_VERSION,
            "model": settings.llm_model,
            "job_type_metric": f"containment, answer <= label + {JOB_TYPE_EXTRA_WORDS} word",
        },
    )
    print(f"\n{format_gate_summary(gate)}")
    assert gate.passes, gate.mean_accuracy


def test_regression_guard_on_the_tuning_set() -> None:
    llm = build_llm(get_settings())
    if llm is None:
        pytest.skip("no LLM provider configured; set up Bedrock per docs/10")

    report = run_eval(llm, load_golden_set())
    write_report(report)
    print(f"{format_comparison(report)}\n\nfield accuracy: {report.field_accuracy}")
    assert report.passes, report.field_accuracy
