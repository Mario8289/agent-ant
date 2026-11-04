# Evals

Golden sets and evaluation suites. Kept apart from unit tests because evals are slow, cost
money, and are non-deterministic — they never run in the default `just test`.

| Path | Contents |
|---|---|
| `datasets/` | Hand-labelled messages (synthetic, or consented and anonymised) |
| `suites/` | Scoring code and fixtures |
| `reports/` | Generated results (gitignored) |

Built in Week 3 (issues #25, #26).
