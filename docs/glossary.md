---
title: Glossary
status: draft
version: 0.1
last_updated: 2026-11-06
---

# Glossary

Plain-English definitions of the terms used in these docs and the code. Each entry says
where it first matters, so you can find the context.

## Telephony

**Call forwarding (unconditional)**
Every incoming call goes to another number. The iPhone's Call Forwarding setting does this.
It is not what the wedge needs.

**Call forwarding (conditional, no answer)**
Calls go to another number only when the phone is not answered after a set time. This is what
G0b tests. See [08](./08-telephony-forwarding-test.md).

**GSM codes (MMI codes)**
Dial codes such as `**61*number#` that set call forwarding on the phone's network. They work
through the phone app, not through Twilio. Carriers can vary them.

**Ring time**
How long the phone rings before a no-answer forward starts. Set in seconds (5 to 30).

**Caller ID**
The number that appears as the caller. For this product it matters because a missed call must
be matched to the caller's number. Twilio puts it in the **From** field.

**E.164 format**
The international phone number format, such as `+447533021710`. Use it in code and config.

**Number region (US1, IE1)**
Where Twilio processes and stores data for a number. The UK has no Twilio region, so Ireland
(IE1) is the nearest European option. See the open question on R4.

**Trial account**
Twilio's free tier. It limits which numbers you can buy and who you can call or message. See
the Free units page for the limits.

**Regulatory bundle**
The address and identity checks Twilio needs before a UK number can be bought or used.

## Twilio

**Webhook**
A URL on your server that Twilio calls when something happens, such as a call or a message
arriving. The app will expose these.

**TwiML**
Twilio's response language. An XML file that tells Twilio what to do with a call or message:
play audio, forward, record, and so on.

**TwiML Bin**
A TwiML script stored inside the Twilio console. It runs without any server code. Used for the
G0b test. It is replaced by the real webhook later.

**A call comes in**
The setting on a phone number that says what Twilio does with an incoming call: a webhook, a
TwiML Bin, or something else.

**Call log**
Twilio's record of each call, including the From, To, duration and status. Found under
Monitor → Logs → Calls.

**Debugger / Monitor**
Where Twilio shows errors and logs. Check here first when a test fails.

## Product and architecture

**Missed-call → booked-job**
The product's wedge. A missed call triggers a fixed SMS and creates a job record for the
tradesperson to approve.

**Idempotency**
Doing the same thing twice has the same effect as doing it once. Twilio can resend a webhook,
so the app stores each provider ID as a unique key and ignores repeats. See D-005 and
[05](./05-architecture-and-schema.md).

**Persist before processing**
Save the raw incoming event to the database before doing anything else with it. If the app
crashes, the event is still there. See `AGENTS.md` rule 2.

**Pydantic**
A Python library that checks data against a model. Used at every boundary: webhook payloads,
LLM output and database records.

**StateGraph (LangGraph)**
A workflow written as nodes and edges, with conditional branches. It is how the missed-call
agent is structured. See [ADR 0001](./adr/0001-orchestration-langgraph.md).

**Checkpointer**
Saves a LangGraph run's state to Postgres, so a run can resume after a restart.

**Human-in-the-loop (`interrupt()`)**
The graph pauses and waits for a person to approve, edit or reject a job before continuing.

**Golden set**
A hand-labelled set of example messages with the correct answers. Used to measure whether the
LLM extracts fields correctly. Stored in `evals/datasets/` once it exists.

**DPA (Data Processing Agreement)**
A contract that makes a supplier a processor of personal data. Required before live customer
data goes to Twilio or an LLM provider. See R4 and [ADR 0002](./adr/0002-llm-provider.md).

**Bedrock API key**
A bearer token generated in the AWS console for Amazon Bedrock. Set as
`AWS_BEARER_TOKEN_BEDROCK`. Different from an access key ID and secret.

**Synthetic data**
Made-up test data. Only synthetic data may be used in development until a DPA is in place.

## Process

**Gate (G0a, G0b, G0c)**
A pass/fail check that must pass before build work starts. See
[00 §6](./00-business-plan.md).

**Resolution comment**
A comment on a closed issue that links the PR and the files that resolved it. Required by
`AGENTS.md`.

**Branch protection**
A GitHub rule that stops a PR merging unless the required `check` job passes.
