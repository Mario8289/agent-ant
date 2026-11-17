---
id: D-020
title: "Production hosting: AWS App Runner (containers) for the stateless API (#29)"
status: accepted
date: 2026-11-13
---

# D-020 — Production hosting: AWS App Runner (containers) for the stateless API (#29)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap — the app is host-agnostic; a move is a deploy-config swap plus re-pointing
  the same env vars. The sticky choices (Supabase, Bedrock) are orthogonal and unchanged.

## Context

#29 (deployment) needed a home for the stateless FastAPI app. Spike 07 compared
Vercel, AWS App Runner, ECS Fargate, Fly.io, Render and Railway against the workload's real
constraints, not platform marketing. Two requirements rule out serverless: the in-process
`BackgroundTasks` (extraction + SMS send run after the 200, in the same process) and LangGraph
`interrupt()` (D-008, a human-approval run is held and resumed by a live process). Vercel runs
Python/FastAPI but its serverless model reclaims the process after the response, cutting off
exactly that work.

## Decision

Host the API on **AWS App Runner** — managed, long-running containers, no
Kubernetes. The database stays Supabase (docs/design/design-doc.md) and the LLM stays Bedrock (D-018); this
decision is only the stateless app layer. Rationale: a long-running process fits the code as
written, it is the same AWS account as Bedrock (one bill, one IAM story), and the Activate
credits offset hosting. Fly.io and Render are the accepted fallback.

## Consequences

- New `Dockerfile` and `.dockerignore`; an ECR repository; an App Runner service with a
  `/ready` readiness check (DB connectivity) alongside the existing `/health`.
- Bedrock auth moves from `AWS_PROFILE` (`~/.aws/credentials`) to an **App Runner instance
  role** with the Bedrock invoke permission — boto3's default credential chain picks up the
  role, so no AWS keys live in the container.
- Secrets (Twilio, `DATABASE_URL`) are injected as App Runner environment variables, sensitive
  values referenced from Secrets Manager. Migrations run against Supabase as a separate step.
- The app is stateless and Dockerized, so moving to Fly.io or Render later is a config change,
  not a rewrite (spike 07).

## Source

Founder decision, 2026-11-13; spike 07; docs/planning/grants.md (Activate credits), D-005, D-008,
D-018.
