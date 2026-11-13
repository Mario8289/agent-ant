"""Tests for the scoring logic — deterministic, no provider and no cost.

Marked ``eval`` so it stays out of ``just test``, but it exercises the harness without needing a
real model: golden-set loading, field correctness, aggregation and the pass line.
"""

import json

import pytest

from agent_ant_core.llm import JobExtraction
from evals.suites.scoring import (
    DATASET_V2,
    JOB_TYPE_THRESHOLD,
    URGENCY_THRESHOLD,
    EvalReport,
    ExampleResult,
    GateReport,
    aggregate,
    field_correct,
    format_comparison,
    format_gate_summary,
    format_misses,
    job_type_correct,
    load_golden_set,
    meets_thresholds,
    run_gate,
    score_example,
)

pytestmark = pytest.mark.eval


def test_golden_set_loads_with_expected_examples() -> None:
    examples = load_golden_set()
    assert len(examples) >= 20


def test_every_example_has_all_label_fields() -> None:
    for example in load_golden_set():
        assert set(example.label) == {"name", "job_type", "location", "urgency", "preferred_date"}


def test_field_correct_handles_absent_and_present() -> None:
    assert field_correct(None, None) is True
    assert field_correct("Leeds", None) is False
    assert field_correct(None, "Leeds") is False
    assert field_correct("Leeds", "Leeds") is True
    assert field_correct("  Leeds ", "leeds") is True  # normalised


def test_score_example_compares_every_field() -> None:
    extraction = JobExtraction(name="Sam", job_type="wardrobe fitting", urgency="high")
    label = {
        "name": "Sam",
        "job_type": "wardrobe fitting",
        "location": None,
        "urgency": "high",
        "preferred_date": None,
    }
    assert score_example(extraction, label) == {
        "name": True,
        "job_type": True,
        "location": True,  # both absent
        "urgency": True,
        "preferred_date": True,  # both absent
    }


def test_score_example_marks_mismatches_wrong() -> None:
    extraction = JobExtraction(job_type="tiling", urgency="low")
    label = {
        "name": None,
        "job_type": "tap repair",
        "location": "LS2",
        "urgency": "high",
        "preferred_date": None,
    }
    scores = score_example(extraction, label)
    assert scores["job_type"] is False
    assert scores["urgency"] is False
    assert scores["location"] is False  # label has LS2, extraction missed it
    assert scores["name"] is True  # both absent


def test_aggregate_computes_fraction_correct() -> None:
    def scores(job_type: bool, urgency: bool) -> dict[str, bool]:
        return {
            "name": True,
            "job_type": job_type,
            "location": True,
            "urgency": urgency,
            "preferred_date": True,
        }

    accuracy = aggregate(
        [scores(True, True), scores(True, False), scores(False, True), scores(True, True)]
    )
    assert accuracy["job_type"] == 0.75
    assert accuracy["urgency"] == 0.75


def test_thresholds_are_within_bounds() -> None:
    assert 0.0 <= JOB_TYPE_THRESHOLD <= 1.0
    assert 0.0 <= URGENCY_THRESHOLD <= 1.0


def test_format_misses_lists_wrong_fields_only() -> None:
    label = {"name": None, "job_type": "boiler repair", "location": None, "urgency": "high"}
    got = {"name": None, "job_type": "boiler service", "location": None, "urgency": "high"}
    correct = {"name": True, "job_type": False, "location": True, "urgency": True}
    report = EvalReport(
        total=1,
        field_accuracy={},
        results=(ExampleResult("boiler gone", label, got, correct),),
    )
    text = format_misses(report)
    assert "expected 'boiler repair', got 'boiler service'" in text
    assert "urgency" not in text


def test_job_type_accepts_extra_words_up_to_the_cap() -> None:
    assert job_type_correct("decking installation", "decking") is True
    assert job_type_correct("skirting board fitting", "skirting boards") is True  # plural
    assert job_type_correct("Wardrobe  Fitting", "wardrobe fitting") is True  # case, spacing


def test_job_type_rejects_a_missing_label_word() -> None:
    assert job_type_correct("wardrobe installation", "bespoke wardrobe") is False
    assert job_type_correct("worktop installation", "kitchen worktop") is False


def test_job_type_rejects_answers_over_the_length_cap() -> None:
    assert job_type_correct("door hanging and frame repair", "door") is False
    assert job_type_correct("floor tiling", "tiling") is True  # exactly one extra word


def test_job_type_handles_absent_values() -> None:
    assert job_type_correct(None, None) is True
    assert job_type_correct("tiling", None) is False
    assert job_type_correct(None, "tiling") is False


def test_golden_v2_is_a_held_out_set_of_at_least_forty() -> None:
    v2 = load_golden_set(DATASET_V2)
    assert len(v2) >= 40
    v1_messages = {e.message for e in load_golden_set()}
    assert not v1_messages & {e.message for e in v2}, "v2 must not reuse v1 messages"
    assert len({e.message for e in v2}) == len(v2)


def test_golden_v2_labels_follow_the_convention() -> None:
    for example in load_golden_set(DATASET_V2):
        label = example.label
        assert set(label) == {"name", "job_type", "location", "urgency", "preferred_date"}
        assert label["urgency"] in {"low", "medium", "high", "unknown"}
        job_type = label["job_type"]
        assert job_type is None or 1 <= len(job_type.split()) <= 4, example.message
        assert job_type is None or job_type == job_type.lower(), example.message


def test_format_comparison_shows_every_message_and_marks_wrong_fields() -> None:
    label = {"name": None, "job_type": "boiler repair", "urgency": "high"}
    wrong = {"name": None, "job_type": "boiler service", "urgency": "high"}
    right = {"name": None, "job_type": "boiler repair", "urgency": "high"}
    report = EvalReport(
        total=2,
        field_accuracy={},
        results=(
            ExampleResult(
                "first", label, wrong, {"name": True, "job_type": False, "urgency": True}
            ),
            ExampleResult(
                "second", label, right, {"name": True, "job_type": True, "urgency": True}
            ),
        ),
    )
    text = format_comparison(report)
    assert "[MISS] first" in text
    assert "[OK  ] second" in text
    assert text.count("✗") == 1
    assert "got='boiler service'" in text


class _ScriptedModel:
    """Answers every extraction with the same JSON, counting calls."""

    def __init__(self, job_type: str, urgency: str) -> None:
        self.reply = json.dumps(
            {
                "name": None,
                "job_type": job_type,
                "location": None,
                "urgency": urgency,
                "preferred_date": None,
            }
        )
        self.calls = 0

    def complete(self, prompt: str) -> str:
        self.calls += 1
        return self.reply


def _accuracy(job_type: float, urgency: float) -> dict[str, float]:
    return {
        "name": 1.0,
        "job_type": job_type,
        "location": 1.0,
        "urgency": urgency,
        "preferred_date": 1.0,
    }


def test_meets_thresholds_is_inclusive_at_the_line() -> None:
    assert meets_thresholds(_accuracy(JOB_TYPE_THRESHOLD, URGENCY_THRESHOLD)) is True
    assert meets_thresholds(_accuracy(JOB_TYPE_THRESHOLD - 0.001, 1.0)) is False
    assert meets_thresholds(_accuracy(1.0, URGENCY_THRESHOLD - 0.001)) is False


def test_gate_passes_on_the_mean_not_on_the_best_run() -> None:
    def run(job_type: float) -> EvalReport:
        return EvalReport(total=40, field_accuracy=_accuracy(job_type, 1.0))

    assert GateReport(runs=(run(0.85), run(0.85), run(0.70))).passes is True  # mean 0.80
    assert GateReport(runs=(run(1.0), run(0.70), run(0.65))).passes is False  # mean 0.783


def test_run_gate_repeats_the_whole_set() -> None:
    examples = load_golden_set()[:3]
    model = _ScriptedModel("tiling", "unknown")
    gate = run_gate(model, examples, runs=2)
    assert len(gate.runs) == 2
    assert model.calls == 2 * len(examples)


def test_run_gate_needs_at_least_one_run() -> None:
    with pytest.raises(ValueError, match="runs"):
        run_gate(_ScriptedModel("tiling", "unknown"), load_golden_set()[:1], runs=0)


def test_gate_summary_shows_counts_and_no_message_text() -> None:
    examples = load_golden_set()[:2]
    gate = run_gate(_ScriptedModel("tiling", "unknown"), examples, runs=1)
    text = format_gate_summary(gate)
    assert "run 1: job_type" in text
    assert "/2" in text
    assert all(e.message not in text for e in examples)
    assert text.endswith("PASS") or text.endswith("FAIL")
