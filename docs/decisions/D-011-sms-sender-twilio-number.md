---
id: D-011
title: "Auto-SMS sender: Twilio number plus business name in the text (R2)"
status: accepted
date: 2026-11-07
---

# D-011 — Auto-SMS sender: Twilio number plus business name in the text (R2)

- **Date:** 2026-11-07
- **Status:** accepted
- **Reversible?** cheap — the sender is a setting and the wording is one template.

## Context

The auto-text (#20) must come from some sender. The caller phoned Dad's mobile,
the unanswered call was forwarded to a Twilio number, and the text comes from that Twilio
number, so it is a number the caller does not know. R2 (callers ignore or distrust an SMS from
an unknown number) is open, and the founder worried it looks like a scam or invites replies to
the wrong number.

## Decision

Send from the Twilio number and name the business in the fixed template ("Hi,
it's <business>. ... This is our text line: reply with ..."). The sender is configuration,
not code. Revisit only if the caller reply rate (H6) comes in below threshold.

## Consequences

Replies reach the Twilio number, so the reply webhook (#21) works. Options
not taken, per Twilio's own pages (checked 2026-11-07): an alphanumeric sender ID (business
name as sender) is described as one-way, so the caller could not reply and the flow breaks;
porting Dad's mobile number into Twilio would show a number the caller knows, but UK mobile
porting is a manual "custom" process and would redesign the carrier-forwarding approach
(G0b). A Twilio UK mobile (+447) number is a cheaper middle option, not yet checked for cost
or regulatory paperwork. A caller who rings the Twilio number back hears the fixed message
and gets no human.

## Source

founder decision, 2026-11-07; [design doc](../design/design-doc.md) R2;
Twilio alphanumeric sender ID and UK porting guidelines
