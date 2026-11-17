---
id: D-021
title: "Outbound SMS is persisted (`outbound_messages`) with status callbacks and retention (#73)"
status: accepted
date: 2026-11-13
---

# D-021 — Outbound SMS is persisted (`outbound_messages`) with status callbacks and retention (#73)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap — drop a table and the callback route. The only irreversible part is the
  retention decision, which is a policy line, not a schema constraint.

## Context

Outbound SMS was only logged (`logger.info("sms %s accepted")`), never stored.
The product promise is "your missed call gets a text", and we could not prove per call that it
happened, nor see delivery failures without opening Twilio. The reply-rate metric (H6) also
needs a denominator of "texts actually sent". #73 tracked it.

## Decision

- Persist every outbound SMS in a new `outbound_messages` table: `twilio_message_sid` (unique,
  null until Twilio accepts), `raw_event_id` (the triggering inbound event — the missed call
  for the auto-text, or the STOP/HELP reply for a confirmation/help), `to`, `body`, `status`,
  `error_code`, `sent_at`.
- Write the row **before** the Twilio call (the outbound analogue of persist-before-processing),
  then update it with the SID or the error code. A send failure records `status='failed'` plus
  `error_code` (e.g. `21211`), with no SID.
- Twilio's delivery-status callback (`POST /webhooks/sms-status`) updates the row to
  `delivered`/`undelivered`/`failed`, idempotently. The callback URL is passed per message from
  `PUBLIC_BASE_URL`.
- **Retention:** `to` and `body` are personal data, so retain them for **30 days**, then purge
  them (keep `twilio_message_sid` and `status` for aggregate metrics). The purge automation
  rides with #34; the decision is recorded now so the field isn't treated as free to keep.

## Consequences

- "Was this caller texted, and did it deliver?" is answerable from our own database.
- A reply is linked to the specific text that prompted it via `raw_events.related_event_id` →
  `outbound_messages.raw_event_id` (`find_outbound_for_reply`); no redundant column on
  `raw_events`.
- Migration `0006`; the send path now takes a session factory like `extract_reply`, so a
  background send opens its own session.

## Source

#73; founder decision 2026-11-13; D-005 (persist before processing); R4/D-018 (DPA).
