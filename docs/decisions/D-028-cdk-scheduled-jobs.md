---
id: D-028
title: "Schedule the retry and purge commands via CDK (EventBridge Scheduler → ECS Fargate) (#96)"
status: accepted
date: 2026-11-13
---

# D-028 — Schedule the retry and purge commands via CDK (EventBridge Scheduler → ECS Fargate) (#96)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap — `cdk destroy` removes the schedules; the task definitions and roles are
  new.

## Context

D-023, D-024 and D-025 made recovery and retention *commands* (`just retry-sms`,
`retry-extractions`, `purge`) but left the scheduling to "at deploy". App Runner (D-020) has no
native cron, so without something to trigger them a failed send or extraction sits `failed`
forever and outbound `to`/`body` age past 30 days. The founder asked for the scheduler to be
committed as code rather than hand-documented console steps, so it is reviewable and cannot
drift.

## Decision

- Express the scheduler as a **CDK app** in `infra/cdk/` — a standalone uv project, not a
  workspace member — that creates three **EventBridge Scheduler** schedules, each running a
  one-off **ECS Fargate** task on the same image as the API: `retry-sms` and
  `retry-extractions` every ~5 minutes (configurable `retryRateMinutes`), `purge` daily at
  03:00 UTC.
- One task definition per script: EventBridge Scheduler's ECS target cannot override a
  container's command, so the command is baked into the task definition.
- Adopt CDK as the IaC tool **for this stack only**; App Runner, ECR and IAM stay hand-managed
  (D-020) until a separate decision migrates them. A one-time `cdk bootstrap` is a prerequisite.
- Two #96 gaps are folded in: a fully dead-lettered SMS send now alerts the operator via Slack
  (D-026) through an `on_dead_letter` callback on `retry_failed_sends` → `alert_dead_letter`,
  and the dashboard's failed-extractions panel shows the reply body so a dead lead can be read
  without opening the database.
- The `Dockerfile` now copies `scripts/` into the image, so the scheduled tasks can run them.

## Consequences

- The schedules are reviewable, drift-checked (`cdk diff`) and applied with
  `just cdk-synth`/`cdk-diff`/`cdk-deploy`, passing account-specific values as `-c key=value`
  (secrets referenced by Secrets Manager ARN, never committed).
- The Fargate tasks run in the VPC's **public** subnets with a public IP — the pre-live tradeoff
  that avoids NAT and VPC endpoints; revisit before real traffic.
- A lone CDK app for three schedules is a half-migration: it will nag until App Runner/ECR join
  it, and it adds a Node-CLI + `aws-cdk-lib` toolchain that sits outside the workspace.
- `core` still does not import the app layer: the dead-letter hook is a `Callable` passed in, so
  the dependency direction (apps → agents → core) holds.

## Source

#96; founder decision 2026-11-13; D-020, D-023, D-024, D-025, D-026.
