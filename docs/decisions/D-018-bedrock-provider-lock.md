---
id: D-018
title: "LLM provider locked: AWS Bedrock, `eu.anthropic.claude-sonnet-4-6` (R4)"
status: accepted
date: 2026-11-13
---

# D-018 — LLM provider locked: AWS Bedrock, `eu.anthropic.claude-sonnet-4-6` (R4)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap — the seam keeps providers swappable; re-locking another provider means
  re-running the golden set against it.

## Context

R4 (docs/design/design-doc.md) is the risk that free LLM tiers train on customer data. AGENTS.md
rule 5 requires a paid tier with a UK/EU DPA before live traffic. D-009 deferred the
choice: stay provider-agnostic during the MVP, lock one DPA-backed provider before live traffic.
The provider comparison lived in D-009; D-015 and D-016 settled inference geography and model.
The remaining step was the lock itself — confirming the DPA and paid tier, and recording them.

## Decision

Lock **AWS Bedrock** as the extraction provider, model
`eu.anthropic.claude-sonnet-4-6` (D-016). The founder confirms the AWS DPA and UK transfer
addendum are in place against the billed member account `817210752440`, which is pay-as-you-go
(not a free tier). Bedrock carries AWS's contractual no-training commitment — inputs and outputs
are not used to train the models — so R4's exposure is closed. The synthetic-data-only rule is
unchanged: it runs until the live gate, not until this decision.

## Consequences

- R4 moves from "open — deferred to #29" to mitigated (docs/design/design-doc.md). Re-confirm the DPA copy is
  kept and the account remains paid before the first live message; that re-check rides with the
  deployment gate (#29, "paid tier + DPA in place").
- No code change. The Bedrock adapter, `extract_v3` prompt, and the H8a gate already run on
  this exact model, so the lock records what the repo already does rather than changing it.
- The provider seam (`build_llm`) stays. A future model or provider switch is a config change
  plus a golden-set re-run against the new model (D-009), not a schema change.

## Source

Founder confirmation, 2026-11-13; D-009; D-015, D-016;
[Amazon Bedrock data protection](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)
(no training on inputs/outputs).
