"""Scoring for extraction accuracy against the golden set (issue #26, H8).

Exact match per field, normalised (strip + lower), except ``job_type`` which is free text and
uses containment (see ``job_type_correct``). A ``None`` label means "absent": a correct
extraction is also ``None``; filling in an absent field, or missing a present one, counts wrong.
A failed extraction (no valid JSON after repair) scores every field wrong — it was not useful.

The thresholds are constants, frozen by D-017 (``docs/06-decision-log.md``) on 2026-11-13.
D-017 also records that the first scored run happened before any freeze and that the ``job_type``
metric changed after it. The gate is the mean of ``GATE_RUNS`` runs on the held-out ``golden_v2`` set.
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

# job_type is scored by containment: every word of the label must appear in the answer, and the
# answer may be at most this many words longer than the label. The cap stops a rambling answer
# from passing just because it happens to contain the label.
JOB_TYPE_EXTRA_WORDS = 1

# Pass line for H8a (D-017). Do not change these after the gated run; add a new hypothesis row.
JOB_TYPE_THRESHOLD = 0.80
URGENCY_THRESHOLD = 0.90

# A single run is noisy even at temperature 0 (one message is 0.025 at 40 messages), so the gate
# is the mean of this many runs.
GATE_RUNS = 3

DATASET = Path(__file__).resolve().parent.parent / "datasets" / "golden_v1.jsonl"
DATASET_V2 = Path(__file__).resolve().parent.parent / "datasets" / "golden_v2.jsonl"
REPORT_V2 = Path(__file__).resolve().parent.parent / "reports" / "golden_v2.json"
REPORT = Path(__file__).resolve().parent.parent / "reports" / "golden_v1.json"


@dataclass(frozen=True)
class GoldenExample:
    """One labelled message: the raw text and the expected extraction fields."""

    message: str
    label: dict[str, Any]


@dataclass(frozen=True)
class ExampleResult:
    """What the model returned for one message, kept so a failing run can be read, not guessed at."""

    message: str
    label: dict[str, Any]
    got: dict[str, Any] | None  # None when no valid extraction came back after repair
    correct: dict[str, bool]


@dataclass(frozen=True)
class EvalReport:
    """Aggregate accuracy for one run, plus the per-message results behind it."""

    total: int
    field_accuracy: dict[str, float]
    results: tuple[ExampleResult, ...] = ()

    @property
    def passes(self) -> bool:
        return meets_thresholds(self.field_accuracy)

    @property
    def correct_counts(self) -> dict[str, int]:
        """How many messages each field got right, so a report can say 33/40, not just 0.825."""
        return {f: sum(r.correct[f] for r in self.results) for f in FIELDS}


@dataclass(frozen=True)
class GateReport:
    """The gate: several runs of the same prompt on the same set, judged on their mean."""

    runs: tuple[EvalReport, ...]

    @property
    def mean_accuracy(self) -> dict[str, float]:
        return {f: sum(r.field_accuracy[f] for r in self.runs) / len(self.runs) for f in FIELDS}

    @property
    def passes(self) -> bool:
        return meets_thresholds(self.mean_accuracy)


# Means of fractions pick up float error (0.85 + 0.85 + 0.70) / 3 is 0.7999999999999999), which
# would fail a run that exactly meets the line.
_EPSILON = 1e-9


def meets_thresholds(accuracy: dict[str, float]) -> bool:
    """The H8a pass line, applied to either one run or the mean of several."""
    return (
        accuracy["job_type"] >= JOB_TYPE_THRESHOLD - _EPSILON
        and accuracy["urgency"] >= URGENCY_THRESHOLD - _EPSILON
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


def _stem(word: str) -> str:
    return word[:-1] if word.endswith("s") else word


def job_type_correct(predicted: str | None, expected: str | None) -> bool:
    """Containment for the free-text ``job_type`` field.

    Exact match marks "decking installation" wrong for the label "decking", which measures
    wording rather than whether the extraction is useful. Instead every label word (lowercased,
    trailing "s" removed so "boards" matches "board") must appear in the answer, and the answer
    may exceed the label by at most ``JOB_TYPE_EXTRA_WORDS`` words. A missing label word still
    fails, so "wardrobe installation" does not match "bespoke wardrobe".
    """
    if expected is None:
        return predicted is None
    if predicted is None:
        return False
    expected_words = normalize(expected).split()
    predicted_words = normalize(predicted).split()
    if len(predicted_words) > len(expected_words) + JOB_TYPE_EXTRA_WORDS:
        return False
    return {_stem(w) for w in expected_words} <= {_stem(w) for w in predicted_words}


def score_example(extraction: JobExtraction, label: dict[str, Any]) -> dict[str, bool]:
    """Per-field correctness for one extraction against its label."""
    predicted = extraction.model_dump()
    return {
        field: (job_type_correct if field == "job_type" else field_correct)(
            predicted.get(field), label.get(field)
        )
        for field in FIELDS
    }


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
    results: list[ExampleResult] = []
    for example in examples:
        result = extract_job(
            llm,
            example.message,
            extract_prompt=extract_prompt,
            repair_prompt=repair_prompt,
            prompt_version=EXTRACT_PROMPT_VERSION,
            max_repairs=max_repairs,
        )
        correct: dict[str, bool]
        got: dict[str, Any] | None
        if result.job is None:
            # No valid extraction: nothing matched, so every field is wrong.
            correct = dict.fromkeys(FIELDS, False)
            got = None
        else:
            correct = score_example(result.job, example.label)
            got = result.job.model_dump()
        scores.append(correct)
        results.append(ExampleResult(example.message, example.label, got, correct))
    return EvalReport(total=len(examples), field_accuracy=aggregate(scores), results=tuple(results))


def run_gate(llm: LLM, examples: list[GoldenExample], runs: int = GATE_RUNS) -> GateReport:
    """Run the whole set ``runs`` times and keep every run, so variance is visible."""
    if runs < 1:
        raise ValueError("runs must be >= 1")
    return GateReport(runs=tuple(run_eval(llm, examples) for _ in range(runs)))


def format_gate_summary(gate: GateReport) -> str:
    """Counts and the mean per gated field, deliberately without per-message answers.

    The held-out set is only held out while nobody tunes against it. The per-message detail goes
    to the report file, to be read after the gate has been recorded.
    """
    lines: list[str] = []
    for number, run in enumerate(gate.runs, start=1):
        counts = run.correct_counts
        lines.append(
            f"run {number}: job_type {counts['job_type']}/{run.total}, "
            f"urgency {counts['urgency']}/{run.total}"
        )
    mean = gate.mean_accuracy
    verdict = "PASS" if gate.passes else "FAIL"
    lines.append(
        f"mean : job_type {mean['job_type']:.3f} (>= {JOB_TYPE_THRESHOLD}), "
        f"urgency {mean['urgency']:.3f} (>= {URGENCY_THRESHOLD}) -> {verdict}"
    )
    return "\n".join(lines)


def format_comparison(report: EvalReport) -> str:
    """Every message with its label beside the model's answer; a ✗ marks each wrong field."""
    lines: list[str] = []
    for number, result in enumerate(report.results, start=1):
        status = "OK  " if all(result.correct.values()) else "MISS"
        lines.append(f"\n{number:>2}. [{status}] {result.message}")
        if result.got is None:
            lines.append("      no valid extraction")
            continue
        lines.extend(
            f"    {'' if result.correct[field] else '✗'}".ljust(6)
            + f"{field:<15}label={result.label[field]!r:<30} got={result.got[field]!r}"
            for field in result.label
        )
    return "\n".join(lines)


def format_misses(report: EvalReport) -> str:
    """Human-readable list of every wrong field: the message, what was expected, what came back."""
    lines: list[str] = []
    for result in report.results:
        wrong = [field for field, ok in result.correct.items() if not ok]
        if not wrong:
            continue
        lines.append(f"\n{result.message!r}")
        if result.got is None:
            lines.append("    no valid extraction")
            continue
        lines.extend(
            f"    {field}: expected {result.label[field]!r}, got {result.got[field]!r}"
            for field in wrong
        )
    return "\n".join(lines) or "no misses"


def write_report(report: EvalReport, path: Path = REPORT) -> None:
    """Write the report as JSON (gitignored)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "total": report.total,
                "field_accuracy": report.field_accuracy,
                "passes": report.passes,
                "results": [
                    {
                        "message": r.message,
                        "label": r.label,
                        "got": r.got,
                        "correct": r.correct,
                    }
                    for r in report.results
                ],
            },
            indent=2,
        )
    )


def write_gate_report(gate: GateReport, meta: dict[str, Any], path: Path = REPORT_V2) -> None:
    """Write every run, with the prompt, model, dataset and metric that produced it (gitignored)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                **meta,
                "mean_accuracy": gate.mean_accuracy,
                "passes": gate.passes,
                "runs": [
                    {
                        "field_accuracy": run.field_accuracy,
                        "correct_counts": run.correct_counts,
                        "results": [
                            {
                                "message": r.message,
                                "label": r.label,
                                "got": r.got,
                                "correct": r.correct,
                            }
                            for r in run.results
                        ],
                    }
                    for run in gate.runs
                ],
            },
            indent=2,
        )
    )
