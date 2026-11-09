"""Tests for the scoring logic — deterministic, no provider and no cost.

Marked ``eval`` so it stays out of ``just test``, but it exercises the harness without needing a
real model: golden-set loading, field correctness, aggregation and the pass line.
"""

import pytest

from agent_ant_core.llm import JobExtraction
from evals.suites.scoring import (
    JOB_TYPE_THRESHOLD,
    URGENCY_THRESHOLD,
    aggregate,
    field_correct,
    load_golden_set,
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
