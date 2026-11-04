# Extraction prompt — v1

Status: placeholder. The real prompt is written in Week 2 (issue #23).

Prompts are versioned files. Whenever this prompt changes in a way that can change output,
bump the version and record it in the `LLMOutputAudit` row (`prompt_version`) so accuracy
changes can be attributed.

Rules the prompt must respect:

- Extract only: `name`, `job_type`, `location`, `urgency`, `preferred_date`.
- Never produce `caller_number` or `received_at`; those come from the provider.
- Return `unknown` rather than guessing.
- Output must validate against `agent_ant_missed_call.schemas.JobRecord`.
