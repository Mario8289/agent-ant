# Evals

Golden sets and evaluation suites. Kept apart from unit tests because evals are slow, cost
money, and are non-deterministic — they never run in the default `just test`. Run them with
`just eval` (needs a configured LLM provider; see `docs/10`).

| Path | Contents |
|---|---|
| `datasets/golden_v1.jsonl` | 20 hand-labelled synthetic messages. The prompt was tuned on these: a regression guard, not gate evidence |
| `datasets/golden_v2.jsonl` | 40 held-out messages, drafted from the labelling convention without looking at model output. Review the labels before freezing; do not tune the prompt against them |
| `suites/scoring.py` | Scoring, aggregation, thresholds and the report writer |
| `suites/test_scoring.py` | Deterministic harness tests (no provider, no cost) |
| `suites/test_extraction_run.py` | The real scored runs (gate on `golden_v2`, regression guard on `golden_v1`) — skip without a provider |
| `reports/` | Generated results (gitignored) |

## Scoring

Exact match per field (`name`, `location`, `urgency`, `preferred_date`), normalised (strip +
lower). `job_type` is free text, so it uses containment: every word of the label must appear in
the answer, and the answer may be at most one word longer than the label. `null` means "absent";
a failed extraction scores every field wrong.

## The gate (H8a, D-017)

`test_gate_on_the_held_out_set` runs `golden_v2` three times and judges the **mean**: `job_type`
≥ 0.80 and `urgency` ≥ 0.90. It prints counts only, never per-message answers, so the held-out set
stays held out; read `reports/golden_v2.json` after the gate has been recorded. The pass line is
frozen by D-017 on 2026-11-13, after the `golden_v2` labels were signed off. Changing the prompt after seeing the
gate result spends `golden_v2`: a third set is needed before claiming a pass.

`test_regression_guard_on_the_tuning_set` runs `golden_v1` once and prints every message beside its
label. The prompt was tuned on it, so it only guards against regressions.

## Labelling convention

Apply this to every new message, and write the label before looking at any model output.

- `job_type`: two or three lowercase words naming the work. Keep a word that changes the kind of
  work ("bespoke wardrobe"). Never a room, quantity, symptom, or "quote"/"new"/"fix".
- Where the message names the work with a verb ("replaced", "fitted", "repair"), the label uses the same verb as a noun ("replacement", "fitting", "repair").
- `location`: every place detail the customer gave (town and postcode). Never a room or part of
  a property.
- `urgency`: `low`/`medium`/`high` only if the customer says so in words or describes an
  emergency happening now; otherwise `unknown`. A wanted date alone is not urgency.

`golden_v1` predates this convention. One label ("kitchen worktop") breaks the room rule and is
a known miss; do not relabel it to fit the model.

The golden set is synthetic only (rule 5). Consented, anonymised real replies are added once
Dad goes live, in a later set — the harness already loads any JSONL path, so a second set is a
new file, not a code change.
