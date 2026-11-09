"""Scoring for extraction accuracy against the golden set (issue #26, H8).

Exact match per field, normalised (strip + lower). A ``None`` label means "absent": a correct
extraction is also ``None``; filling in an absent field, or missing a present one, counts wrong.
A failed extraction (no valid JSON after repair) scores every field wrong — it was not useful.

The thresholds are constants, frozen before the first scored run (hypothesis-table rule 1).
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_ant_core.llm import LLM, JobExtraction, extract_job
from agent_ant_missed_call.prompts import (
    EXTRACT_PROMPT_VERSION,
    REPAIR_PROMPT_VERSION,
    load_prompt,
)

FIELDS = ("name", "job_type", "location", "urgency", "preferred_date")

# H8 gates on job_type + urgency. "callback" in the H8 row was a stale field name — the current
# extraction schema has no callback field, so the gate is job_type + urgency.
GATE_FIELDS = ("job_type", "urgency")

# PROPOSED thresholds — agree before the first real scored run, then freeze (H8, #26).
JOB_TYPE_THRESHOLD = 0.80
URGENCY_THRESHOLD = 0.90

DATASET = Path(__file__).resolve().parent.parent / "datasets" / "golden_v1.jsonl"
REPORT = Path(__file__).resolve().parent.parent / "reports" / "golden_v1.json"


@dataclass(frozen=True)
class GoldenExample:
    """One labelled message: the raw text and the expected extraction fields."""

    message: str
    label: dict[str, Any]


@dataclass(frozen=True)
class EvalReport:
    """Aggregate accuracy for one run."""

    total: int
    field_accuracy: dict[str, float]

    @property
    def passes(self) -> bool:
        return (
            self.field_accuracy["job_type"] >= JOB_TYPE_THRESHOLD
            and self.field_accuracy["urgency"] >= URGENCY_THRESHOLD
        )


def load_golden_set(path: Path = DATASET) -> list[GoldenExample]:
    """Load the hand-labelled set (one JSON object per line)."""
    examples: list[GoldenExample] = []
    for line in path.read_text().splitlines():
        row = json.loads(line)
        examples.append(GoldenExample(message=row["message"], label=row["label"]))
    return examples


def normalize(value: str) -> str:
    return value.strip().lower()


def field_correct(predicted: str | None, expected: str | None) -> bool:
    """Exact match after normalisation, with ``None`` meaning "absent"."""
    if expected is None:
        return predicted is None
    if predicted is None:
        return False
    return normalize(predicted) == normalize(expected)


def score_example(extraction: JobExtraction, label: dict[str, Any]) -> dict[str, bool]:
    """Per-field correctness for one extraction against its label."""
    predicted = extraction.model_dump()
    return {field: field_correct(predicted.get(field), label.get(field)) for field in FIELDS}


def aggregate(scores: list[dict[str, bool]]) -> dict[str, float]:
    """Fraction correct per field, across all scored examples."""
    if not scores:
        return dict.fromkeys(FIELDS, 0.0)
    return {field: sum(s[field] for s in scores) / len(scores) for field in FIELDS}


def run_eval(llm: LLM, examples: list[GoldenExample], max_repairs: int = 2) -> EvalReport:
    """Run extraction on every example and score the result."""
    extract_prompt = load_prompt(EXTRACT_PROMPT_VERSION)
    repair_prompt = load_prompt(REPAIR_PROMPT_VERSION)
    scores: list[dict[str, bool]] = []
    for example in examples:
        result = extract_job(
            llm,
            example.message,
            extract_prompt=extract_prompt,
            repair_prompt=repair_prompt,
            prompt_version=EXTRACT_PROMPT_VERSION,
            max_repairs=max_repairs,
        )
        if result.job is None:
            # No valid extraction: nothing matched, so every field is wrong.
            scores.append(dict.fromkeys(FIELDS, False))
        else:
            scores.append(score_example(result.job, example.label))
    return EvalReport(total=len(examples), field_accuracy=aggregate(scores))


def write_report(report: EvalReport, path: Path = REPORT) -> None:
    """Write the report as JSON (gitignored)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "total": report.total,
                "field_accuracy": report.field_accuracy,
                "passes": report.passes,
            },
            indent=2,
        )
    )
