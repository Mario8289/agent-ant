# Spike 05: LangGraph branch, interrupt and checkpointer resume (#61)

A synthetic message runs `extract -> validate -> interrupt -> approve`, and the run resumes
from a Postgres checkpoint, even from a brand-new process. Synthetic data only.

```
extract -> validate --valid--> human_review (interrupt) --> approved | rejected
                    \--invalid--> flag_for_human ---------> needs_review
```

| File | Purpose |
|---|---|
| `review_graph.py` | The `StateGraph`: conditional edge on validity, `interrupt()` for approval |
| `test_review_graph.py` | 6 tests against a real Postgres checkpointer |
| `docker-compose.yml` | Throwaway Postgres on port **5434** |

## Run the tests

LangGraph is deliberately **not** added to the repo's dependencies yet. ADR 0001 keeps it inside
`agents/missed_call` from Week 2, so the spike pulls it in for one run with `uv --with`. This
changes neither `pyproject.toml` nor `uv.lock`.

From the repo root:

```bash
# 1. start Postgres (waits until healthy)
docker compose -f spikes/05-langgraph-branch/docker-compose.yml up -d --wait

# 2. run the tests (defaults to localhost:5434, the compose file's port)
cd spikes/05-langgraph-branch
uv run --all-packages --with langgraph --with langgraph-checkpoint-postgres pytest -v

# 3. clean up (removes the container and its data)
cd ../..
docker compose -f spikes/05-langgraph-branch/docker-compose.yml down
```

Expected: `6 passed`. Tested with `langgraph` 1.2.20 and `langgraph-checkpoint-postgres` 3.2.0.
Pin both when this moves into `agents/missed_call` (ADR 0001).

## "6 skipped" means Postgres was not reached

If the database is unreachable the tests **skip**; they do not pass or fail. Check the summary
line. The skip reason names the host and port that was tried. Set `DATABASE_URL` only to point
somewhere else.

## What the tests touch

`PostgresSaver.setup()` creates LangGraph's checkpoint tables (`checkpoints`, `checkpoint_blobs`,
`checkpoint_writes`, `checkpoint_migrations`) in whichever database is used. Each test uses a
fresh random `thread_id`, so nothing is truncated. Use the throwaway container.

## Things worth knowing

- **Resume re-runs the interrupted node from its first line.** Anything before `interrupt()` in
  `human_review` must be safe to repeat, so it does no side effects first. Finished nodes
  (`extract`, `validate`) are not re-run; the restart test asserts the extractor is called 0 times
  after resume.
- **Approval is the only path to `approved`.** An invalid extraction goes to `needs_review` and
  never reaches the interrupt (rule 6).
- **Extraction is a plain injected function**, so the graph tests need no LLM. Wiring spike 04's
  repair loop in as that function is #23.
