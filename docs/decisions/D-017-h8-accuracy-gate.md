---
id: D-017
title: "H8 accuracy gate: containment metric for `job_type`, held-out `golden_v2`, frozen pass line (H8a)"
status: accepted
date: 2026-11-13
---

# D-017 — H8 accuracy gate: containment metric for `job_type`, held-out `golden_v2`, frozen pass line (H8a)

- **Date:** 2026-11-13
- **Status:** accepted (2026-11-13). The founder reviewed and approved the `golden_v2` labels;
  the pass line is frozen from this date, before the gated run.
- **Reversible?** cheap — scoring constants and the dataset path, but changing the pass line after
  the gated run invalidates that run.

## Context

Hypothesis-table rule 1 says to freeze the pass line before the test starts. That
did not happen for H8: the line was only ever "proposed" (docs/discovery/hypotheses.md, `scoring.py`), although
`evals/README.md` and the `scoring.py` docstring said "frozen". The first scored run therefore
happened without a freeze. Results on `golden_v1` (20 messages), with counts:

| Prompt | `job_type` metric | `job_type` | `urgency` |
|---|---|---|---|
| `extract_v1` | exact match | 7/20 (0.35) | 16/20 (0.80) |
| `extract_v2` | exact match | 12/20 (0.60); an earlier run scored 11/20 | 20/20 (1.00) |
| `extract_v2` outputs, rescored | containment | 17/20 (0.85) | 20/20 (1.00) |
| `extract_v3` | containment | 18/20 (0.90) | 20/20 (1.00) |

Three problems with reading those numbers as evidence:
1. **Tuned on the test set.** `extract_v2` and `extract_v3` were written after reading the
   misses on `golden_v1`, then scored on `golden_v1`. The 1.00 urgency score is optimistic.
2. **The metric changed after the results.** Exact match on a free-text field measured wording,
   not usefulness: "decking installation" failed the label "decking". The remaining
   `job_type` misses under exact match were wording differences, with one real loss ("bespoke
   wardrobe" became "wardrobe installation", which dropped the word that matters).
3. **Noise.** One message is 0.05 at 20 messages, and the same prompt scored 11/20 and 12/20.

## Decision

- `job_type` is scored by **containment**: every word of the label (lowercased, trailing "s"
  removed) must appear in the answer, and the answer may be at most **one word longer** than the
  label. Every other field stays exact match. `job_type` stays free text; no category list.
- The gate is **H8a**, run on a new held-out set, `golden_v2` (40 messages, drafted from the
  labelling convention in `evals/README.md` without looking at model output). The gate is the
  **mean of three runs**, with counts reported. Pass line: `job_type` ≥ 0.80 and
  `urgency` ≥ 0.90, unchanged from H8. Prompt `extract_v3`, model
  `eu.anthropic.claude-sonnet-4-6` (D-016).
- `golden_v1` stays as a regression guard. It is not gate evidence.
- H8 keeps its recorded first-run result and is marked superseded (docs/discovery/hypotheses.md, rule 4).
- The gate prints counts only; per-message answers go to `evals/reports/golden_v2.json` and
  are read after the gate is recorded. If the gate fails and the prompt is changed, `golden_v2`
  is spent as a held-out set and a third set is needed before claiming a pass.
- **Result (2026-11-13, one gated run: three passes over `golden_v2`, prompt `extract_v3`, model
`eu.anthropic.claude-sonnet-4-6`):** PASS.

| Run | `job_type` | `urgency` |
|---|---|---|
| 1 | 36/40 | 40/40 |
| 2 | 35/40 | 40/40 |
| 3 | 35/40 | 40/40 |
| Mean | 0.883 (line ≥ 0.80) | 1.000 (line ≥ 0.90) |

Other fields, mean: `name` 0.975, `location` 1.000, `preferred_date` 0.975. The set and prompt
were not changed between freeze and run. Per-message detail:
`evals/reports/golden_v2.json` (gitignored).

## Consequences

The pass tells us the extractor is not obviously broken on messages it was
not tuned on. It does not tell us it is useful: 40 synthetic messages is a smoke test. The real
H8 evidence is the Week 4 edit rate on live replies (#30, #35); until then the golden sets guard
against regression only. One label in `golden_v1` ("kitchen worktop") breaks the "no rooms" rule;
it stays as a known miss rather than being relabelled to fit the model. Rooms are dropped from
`job_type` and are not stored in any field (a separate `room` field would be a schema change).

## Source

First scored runs, 2026-11-09 to 2026-11-13 (`evals/reports/`); hypothesis table
rules 1, 2 and 4; Ries, *The Lean Startup* (2011), innovation accounting
