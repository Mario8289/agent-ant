---
id: D-015
title: "LLM inference: `eu.*` cross-region acceptable, `global.*` rejected"
status: accepted
date: 2026-11-10
---

# D-015 — LLM inference: `eu.*` cross-region acceptable, `global.*` rejected

- **Date:** 2026-11-10
- **Status:** accepted
- **Reversible?** cheap — a config change (`LLM_MODEL` id).

## Context

London (`eu-west-2`) offers only a couple of Claude models in-region, so the
founder wanted a wider choice. Spike 06 found no regulatory blocker: the EU renewed the UK's
adequacy decisions on 19 Dec 2025 (valid to 2031), the UK treats the EEA as adequate, and
Bedrock's `eu.*` cross-region profile stays inside EU geography.

## Decision

Relax D-009's single-region constraint. The `eu.*` cross-region inference profile
is accepted, because prompts and outputs stay within EU geography. `global.*` stays rejected —
it can route to the US (or any region) with no residency guarantee. `AWS_REGION` stays
`eu-west-2`; `LLM_MODEL` may be an `eu.*` profile id.

## Consequences

More models and burst capacity than in-region London. A request may be served
by any EU region in the profile, so data is not pinned to the UK — lawful under UK adequacy,
but not "UK-only". The region SCP and IAM policy must keep allowing the EU regions the profile
routes to and keep blocking `global.*` (docs/runbooks/manual-steps.md, spike 06). Revert to a single-region model id
if a customer later needs UK-only processing.

## Source

spikes/06-uk-eea-data-residency.md; EU adequacy renewal (19 Dec 2025)
