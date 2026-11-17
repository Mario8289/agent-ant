---
title: Trades AI — Documentation Index
status: draft
version: 0.1
last_updated: 2026-11-04
---

# Trades AI — Documentation

Working documents for the **missed-call → booked-job** prototype.
Solo founder, ~2 hrs/day. Design partner: Dad (carpenter, 60) plus 4–5 other tradespeople.

Tracked in [epic #3](https://github.com/Mario8289/agent-ant/issues/3) (initial docs: [#2](https://github.com/Mario8289/agent-ant/issues/2)).

## Business & validation
*Sources: Fitzpatrick (The Mom Test) · Ries (The Lean Startup) · Thiel (Zero to One)*

| # | Document | Purpose | Status |
|---|---|---|---|
| 00 | [Business Plan](./00-business-plan.md) | Thesis, competitors, MVP scope, 6-week sprint, gates | draft |
| 01 | [Hypothesis Table](./01-hypothesis-table.md) | Falsifiable assumptions with committed pass lines | draft |
| 02 | [Mom Test Script — Dad](./02-mom-test-script-dad.md) | Discovery interview script, no pitching | draft |
| 03 | [Requirements Capture Sheet](./03-requirements-capture-sheet.md) | Cross-interview pattern tracking | draft |
| 04 | [Grants Timeline](./04-grants-timeline.md) | When to apply for credits vs. cash grants | draft |

## Architecture
*Sources: Kleppmann (DDIA) · Huyen (AI Engineering) · Lubanovic (FastAPI)*

| # | Document | Purpose | Status |
|---|---|---|---|
| 05 | [Architecture & Schema](./05-architecture-and-schema.md) | Diagram, Pydantic schema, idempotency, risk register | draft |
| 06 | [Decision Log](./06-decision-log.md) | ADR-style records: context, decision, consequences, source. Longer ADRs in [adr/](./adr/README.md) | draft |
| 07 | [Learning Track](./07-learning-track.md) | Precursor skills in order, each with a "done when" test | draft |
| 11 | [Request Flows](./11-request-flows.md) | Sequence diagrams per webhook: order, systems, code anchors | draft |

## Testing & reference

| Document | Purpose | Status |
|---|---|---|
| [08 — Telephony Forwarding Test](./08-telephony-forwarding-test.md) | G0b runbook: Twilio setup, iPhone no-answer codes, pass/fail | draft |
| [09 — Execution Plan](./09-execution-plan.md) | What to do next, in order, week by week, with the gates | draft |
| [10 — Manual Steps](./10-manual-steps.md) | Console clicks and real-world steps only you can do, with what each blocks | draft |
| [12 — Agent Roadmap](./12-agent-roadmap.md) | Ranked agents after `missed_call`, grouped into roles; planned, not built (D-031) | draft |
| [Glossary](./glossary.md) | Plain-English definitions: telephony, Twilio, product and process terms | draft |

Longer decisions live in [adr/](./adr/README.md):

| ADR | Decision | Status |
|---|---|---|
| [0001](./adr/0001-orchestration-langgraph.md) | Orchestration: LangGraph for the missed-call agent | accepted |
| [0002](./adr/0002-llm-provider.md) | LLM provider: swappable for the MVP, DPA-backed lock before live | accepted |

## Status key

- **draft** — not yet tested against evidence
- **validated** — supported by interview or usage data
- **superseded** — replaced; kept for history

## ✅ Verification status

Claims were checked against sources on **2026-11-04** (issue #13). What that covered:

| Category | Status |
|---|---|
| Book quotes and editions | Verified — Fitzpatrick (2013), Ries (2011), Thiel (2014), Huyen (2025), Lubanovic (2024), Kleppmann & Riccomini (2026). Fitzpatrick's "fool's gold" quote corrected to "…shiny, distracting, and worthless" |
| Competitor pricing | Verified against vendor pages — see [00 §3](./00-business-plan.md). Prices change; re-check before quoting |
| Grant and credit terms | Verified against programme pages — see [04](./04-grants-timeline.md). Supabase's startup programme is discontinued |
| Reference repos | Verified — `fastapi/full-stack-fastapi-template` (~46k stars), `langchain-ai/langgraph` (~44k), `drivendataorg/cookiecutter-data-science` (~10k) |
| Twilio webhook behaviour | Verified — form-encoded payloads, `X-Twilio-Signature` validation via the SDK |
| Carrier call forwarding | **Still untested** on Dad's real plan — this is gate G0b (issue #11) and blocks the wedge |

**⚠️ TO CHECK** still appears where a claim has not been confirmed. After this pass, the
only open item is carrier call forwarding — and that is a gate to test (G0b, issue #11), not
desk research.

## Conventions

- Every doc starts with a front-matter block (status, version, sources).
- Layout: Purpose → Content → Anti-patterns → Open questions → Change history.
- Diagrams are Mermaid so they render on GitHub.
- Links are relative so they work locally and on GitHub.
- Business doctrine and architecture are kept in separate documents.
- The decision log is append-only; superseded decisions are marked, not deleted.

## Next actions

Tracked on GitHub under [epic #3](https://github.com/Mario8289/agent-ant/issues/3):

1. Foundation milestone — repo scaffold, tooling, CI, docs housekeeping.
2. Pre-sprint gates — run the discovery interviews (doc 02) and test carrier call forwarding
   to a Twilio number (doc 05, risk R1) **before** any product build hours.
3. ~~Verify each ⚠️ TO CHECK item~~ — done 2026-11-04 (issue #13); see Verification status.
