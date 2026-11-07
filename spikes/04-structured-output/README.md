# Spike 04: structured output with bounded repair (#60)

Messy customer text becomes a validated Pydantic object. If the model's reply is invalid,
the validation errors are fed back for a limited number of repairs, then the message is
flagged instead of looping forever. Synthetic data only.

| File | Purpose |
|---|---|
| `extract.py` | `JobExtraction` model, `extract_job` validate-and-repair loop, `ExtractionResult` (maps onto `LLMOutputAudit`) |
| `prompts/extract_v1.md`, `prompts/repair_v1.md` | Versioned prompt files, not inline strings |
| `test_extract.py` | 11 tests using a scripted fake LLM |

## Run the tests

No database, API key or network needed:

```bash
cd spikes/04-structured-output
uv run --all-packages pytest -v
```

Expected: `11 passed`.

## What it proves, and what it doesn't

- **Proves:** the loop. Valid output passes first time; invalid or non-JSON output is repaired;
  after `max_repairs` it stops with `validated=False` and `job=None` (total calls are at most
  `1 + max_repairs`); `caller_number` in a model reply is rejected (trusted fields never come
  from the LLM).
- **Does not prove:** that any real model produces good extractions. The LLM here is a scripted
  fake behind a one-method `complete(prompt) -> str` interface. Real provider wiring and
  extraction quality (evals) belong to #22 and #23.
