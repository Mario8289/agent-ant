---
id: D-035
title: "Customer-facing AI follows an autonomy ladder"
status: proposed
date: 2026-11-22
---

# D-035 — Customer-facing AI follows an autonomy ladder

- **Date:** 2026-11-22
- **Status:** proposed. The founder agreed Levels 0 and 1 and the design-only treatment of Level 2
  in conversation. The record stays proposed until the open questions below are answered.
- **Reversible?** cheap. Each level is a setting that can be switched off.

## Context

D-004 says the AI never writes free text to customers. That keeps the risk low and the replies
rigid. The Receptionist needs to ask a customer a useful follow-up (what is leaking, which
room) without the trader writing each one. Chat with the AI employees is a different matter: it
is trader-facing, so free-form replies there are fine.

The current Level 0 text (`sms.py`) does not say it is automated: "This is our text line".

## Options considered

| Option | Outcome |
|---|---|
| A Keep D-004 as is, forever | Safe, but the Receptionist can only ever ask one thing |
| **B** (chosen) A ladder, one level at a time, each with its own evidence | Gains capability in steps the trader controls |
| C Let the model write to customers, with approval | Per-message review defeats the point, and a missed review is a trust and consumer-law risk |

## Decision

| Level | What the AI does | Status |
|---|---|---|
| 0 | Fixed template, as built (D-004) | built |
| 1 | The model **picks** from a fixed bank of pre-written clarifying questions. Every word the customer sees was written and reviewed by a human | build in the MVP |
| 2 | The model writes a clarifying question under limits (length, one question, no prices or promises), per-trader opt-in, off by default, behind evals | design only |
| 3 | Fully conversational | not planned |

Rules at every level:
- The first AI-driven message to a customer says it is automated. (Level 0 is checked under the
  open question below.)
- STOP is honoured (D-019).
- Every message sent is stored verbatim for audit (D-021).
- The trader can take over a conversation.
- Level 1 questions are chosen by ID. The model's output is validated against the bank, and an
  unknown ID is rejected.
- Level 2 needs an eval suite and a pass line fixed in advance before it can be turned on for any
  trader.

## Consequences

- A question bank and a picker are built for Level 1. No customer-facing prose is generated.
- Trader-facing chat is unrestricted, because nothing there reaches a customer.
- Level 2 stays unbuilt, and its design is recorded for when evidence supports it.

## Open questions

- **Does Level 1 count as consistent with D-004?** The words are pre-written, so the argument is
  yes. Founder to confirm.
- **Should the Level 0 text say it is automated?** The wording today does not. Founder to decide,
  with the PECR and consumer-law reading in the consent spike (#127).

## Source

Founder decision, 2026-11-22; D-004, D-019, D-021; [roadmap](../product/roadmap.md) open
question on D-004 and quotes.
