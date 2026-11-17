---
id: D-016
title: "Extraction model: Claude Sonnet 4.6 for now (newer models account-gated)"
status: accepted
date: 2026-11-10
---

# D-016 — Extraction model: Claude Sonnet 4.6 for now (newer models account-gated)

- **Date:** 2026-11-10
- **Status:** accepted
- **Reversible?** cheap — a config change (`LLM_MODEL`) plus an IAM resource ARN.

## Context

Enabling Bedrock, the founder found only `eu.anthropic.claude-sonnet-4-6` and
`eu.anthropic.claude-haiku-4-5` actually callable in `eu-west-2`. Sonnet 5, Sonnet 5.5 and
Opus 5.5 all return "not available for this account" — an account-level entitlement, not a
routing limit: the `global.*` profile returns the same error, confirming it is the account,
not the geography.

## Decision

Use `eu.anthropic.claude-sonnet-4-6` for extraction now. It stays in the EU
(D-015) and is strong at structured extraction.

## Consequences

The IAM inline policy `BedrockInvokeEuSonnet55` is scoped to this model's
profile; its name is now stale but harmless. To request newer models, ask AWS Sales/Support for
account `817210752440` (`eu-west-2`, model `eu.anthropic.claude-sonnet-5-5`) — limits usually
relax as a new account builds billing history. When access opens, switching is a one-line
`.env` change plus the IAM policy ARNs (docs/runbooks/manual-steps.md).

## Source

Bedrock model-access test, 2026-11-10; [manual steps](../runbooks/manual-steps.md)
