# Spike 07: Where to host the stateless FastAPI service (#29)

## Question

Where should the API run in production? The candidate list is Vercel, AWS App Runner, AWS ECS
Fargate, Fly.io, Render and Railway. The point of this spike is to make the choice on the
workload's real constraints, not on platform marketing.

## Why it matters

This is a one-way-ish decision: the deploy config, secrets layout and some code (how background
work runs) are shaped by the host, and re-homing later costs a day or more. The database is
already settled as Supabase (docs/05) and the LLM is Bedrock on AWS (D-018), so the question is
only the **stateless app layer**.

## Method

Desk research against the platform docs (Vercel function limits and Python runtime, AWS App
Runner vs Fargate, Fly/Render/Railway), then score each option against the workload's actual
shape. Verified against vendor pages in November 2026.

## The workload

What we actually deploy, so the comparison is against this and not a generic web app:

- **One FastAPI service, Python 3.12**, sync webhook handlers that return 200 fast (rule 2:
  persist → answer).
- **In-process `BackgroundTasks`**: after the 200, the same process runs `extract_reply` (a
  Bedrock call, seconds) and `send_missed_call_sms` (a Twilio call). This is the current
  implementation, not an aspirational one.
- **LangGraph with a Postgres checkpointer and `interrupt()`** (D-008, coming in Week 2/3): a
  human-approval run is *held* and *resumed* by a long-running process. An interrupted graph
  cannot be serialised to a request/response boundary.
- **Two outbound connections**: Supabase Postgres and AWS Bedrock, both over the public
  internet.
- **Server-rendered Jinja2 dashboard** (D-014) — ordinary HTTP, no WebSockets today, but
  nothing rules them out later.

Three hard constraints fall out of that:

1. **A long-running process.** `BackgroundTasks` and `interrupt()` both need a process that
   outlives the HTTP response. Anything that reclaims the process after the response breaks
   them.
2. **Outbound internet** to two third parties (Supabase, Bedrock). Fine everywhere; a VPC-only
   deployment would be a mistake.
3. **Secrets** (Twilio, AWS profile, database URL) injected at deploy time.

## Findings

### Vercel — serverless functions (Python/ASGI runtime)

- Vercel does run FastAPI: the Python runtime serves ASGI apps and the whole FastAPI app builds
  into a single Vercel Function. So "it runs Python" is not the blocker.
- The blocker is the execution model:
  - **Duration caps.** Python functions default to a 60s maximum (raised via `maxDuration`);
    Pro/Enterprise reach 800s, with a 30-minute beta. A Bedrock extraction fits *inside* a
    request, but our extraction runs *after* the response, in a background task.
  - **Background work is reclaimed.** FastAPI's `BackgroundTasks` run in the same process after
    the response returns; on Vercel the function is frozen/reclaimed once the response is sent,
    so the task is cut off. This is a documented, community-confirmed limitation (Vercel issue
    #13166; the standard advice is "use a worker on a container platform or a queue").
  - **`interrupt()` cannot be held.** An interrupted LangGraph run needs a live process to
    resume from the checkpoint when a human approves; serverless has nowhere to hold it.
  - **Cold starts** on every webhook (Twilio at-least-once delivery makes this worse).
- **Verdict:** not fit for the current architecture. It would force moving background work to a
  queue and a separate worker — exactly the outbox work (#34) we deliberately deferred, and a
  break with D-005's one-service simplicity. Vercel is the right answer for a request/response
  web app; this is a background-job service.

### AWS App Runner — managed containers

- Point it at a Docker image (ECR) or a source repo; it builds, runs, autoscales, terminates TLS
  and health-checks the container.
- Pros: **same AWS account as Bedrock** (one IAM story, one bill), **Activate credits cover
  hosting** (docs/04), a long-running container so `BackgroundTasks` and `interrupt()` just
  work, no Kubernetes. Scales to one (or zero) instance; pennies at this volume.
- Cons: AWS-specific config (service + IAM role), less "one command" than Fly/Render, pricing
  less transparent than a flat PaaS.

### AWS ECS Fargate — containers you wire yourself

- Same runtime guarantees as App Runner, but you assemble task definition + service + ALB +
  target group + security groups.
- Pros: full control, same account/credits.
- Cons: strictly more moving parts than App Runner for one service; the extra control is
  speculative at this stage (D-005 is one service, no consensus).

### Fly.io — git-push containers

- `fly launch` from a Dockerfile; runs the container near users, TLS included.
- Pros: best DX of the container options, cheap, scales to zero.
- Cons: a **second cloud** to manage (account, secrets, billing) with **no credits**; the
  stateless app is residency-neutral so this is not a legal problem, only an ops one.

### Render — managed PaaS with long-running web services

- "Web services" are long-running processes (fits `BackgroundTasks`); it also sells "background
  workers" separately but nothing forces us to split.
- Pros: simple git-push, long-running model fits.
- Cons: new account, no credits; second cloud next to AWS.

### Railway — simple container PaaS

- Same shape as Fly/Render: simple, git-push, long-running.
- Cons: new account, no credits; the least differentiated of the simple PaaS trio.

## Conclusion

The decision is really "long-running container" vs "serverless function", and only the former
satisfies constraints 1 (background tasks + `interrupt()`). Vercel, despite running Python, is on
the wrong side of that line.

Among the container hosts, **AWS App Runner** is the front-runner: it gives the long-running
process the app already assumes, sits on the AWS account we already use for Bedrock, and is
covered by the Activate credits. Fly.io and Render are the fallback if the founder wants the
lowest-ops path and accepts a second cloud with no credits; both are fine and the app is
stateless, so the switch is cheap.

## Done when

- [ ] Founder reviews this and picks a host; the choice is recorded as a decision (D-020) with
      this spike cited as the source.
- [ ] After the decision: write the `Dockerfile`, the deploy config for the chosen host, and the
      `docs/10` provisioning steps (Supabase project + connection string, secrets, health check).

## Sources

- Vercel — function duration limits and the Python/ASGI runtime:
  https://vercel.com/docs/functions/configuring-functions/duration ,
  https://vercel.com/docs/functions/runtimes/python ,
  https://vercel.com/docs/frameworks/backend/fastapi
- Vercel background-task limitation (community): https://github.com/vercel/vercel/issues/13166
- AWS App Runner vs Fargate: https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html
- Fly.io: https://fly.io/docs/
- Render: https://render.com/docs
- Repo context: docs/05 (Supabase, one service), D-005, D-008 (LangGraph `interrupt()`),
  D-018 (Bedrock), docs/04 (AWS Activate credits cover hosting), #34 (outbox deferred).
