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

## Status key

- **draft** — not yet tested against evidence
- **validated** — supported by interview or usage data
- **superseded** — replaced; kept for history

## ⚠️ Verification flags

**⚠️ TO CHECK** in any document means the claim has not been confirmed against a source.

| Category | Why unverified |
|---|---|
| Book quotes | Document search unavailable when written; quotes are from general knowledge |
| Competitor pricing | VioTrade, Tradehand etc. come from unverified research |
| Grant terms & amounts | Confirm on each programme's official page before applying |
| GitHub reference repos | Names and star counts unverified |
| Carrier call forwarding | Untested on Dad's actual mobile plan — **blocks the whole wedge** |

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
3. Verify each ⚠️ TO CHECK item, then remove the tag.
