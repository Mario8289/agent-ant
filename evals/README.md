# Evals

Golden sets and evaluation suites. Kept apart from unit tests because evals are slow, cost
money, and are non-deterministic — they never run in the default `just test`. Run them with
`just eval` (needs a configured LLM provider; see `docs/10`).

| Path | Contents |
|---|---|
| `datasets/golden_v1.jsonl` | Hand-labelled synthetic messages (one JSON object per line) |
| `suites/scoring.py` | Scoring, aggregation, thresholds and the report writer |
| `suites/test_scoring.py` | Deterministic harness tests (no provider, no cost) |
| `suites/test_extraction_run.py` | The real scored run — skips without a provider |
| `reports/` | Generated results (gitignored) |

## Scoring

Exact match per field (`name`, `job_type`, `location`, `urgency`, `preferred_date`), normalised
(strip + lower). `null` means "absent"; a failed extraction scores every field wrong. H8 gates
on `job_type` (≥ 0.80) and `urgency` (≥ 0.90) — thresholds are frozen in `scoring.py` before the
first real scored run.

The golden set is synthetic only (rule 5). Consented, anonymised real replies are added once
Dad goes live, in a later set — the harness already loads any JSONL path, so a second set is a
new file, not a code change.
