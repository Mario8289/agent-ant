---
id: D-029
title: "Voicemail-to-text: async Twilio transcription feeds the extraction pipeline (#33)"
status: accepted
date: 2026-11-14
---

# D-029 — Voicemail-to-text: async Twilio transcription feeds the extraction pipeline (#33)

- **Date:** 2026-11-14
- **Status:** accepted
- **Reversible?** cheap — revert the TwiML to the hangup-only version and drop the route; any
  stored `voicemail` rows are inert.

## Context

The funnel only captured a job when the caller *replied to the auto-SMS* (H6).
Callers who would not reply — driving, older, wary of an unfamiliar number — left nothing but a
stored missed call. Week 5 offered an optional "voicemail-to-text" step to widen capture
coverage.

## Decision

- The missed-call TwiML now prompts *"leave a message after the tone"* and uses Twilio's
  `<Record transcribe="true">`. Twilio records the message and, after the caller hangs up,
  asynchronously POSTs the transcript to a new `/webhooks/voicemail-transcription` webhook.
- The transcript is a first-class `raw_events` source (`voicemail`), keyed on `RecordingSid` and
  linked to the missed call by `CallSid` — a stronger link than the SMS reply's number heuristic.
  It runs the **same** extraction pipeline as a reply, so retries, dead-lettering and the
  dashboard failure panel cover voicemail without new machinery.
- The auto-SMS is **kept**: two independent capture paths, not a replacement. A caller who both
  leaves a voicemail and replies to the text produces two captured jobs — the tradesperson
  approves one and rejects the duplicate.
- Transcription uses Twilio's built-in engine (one TwiML attribute, no new infra) and accepts its
  documented American-English-only limitation for now; swap to AWS Transcribe later if UK
  transcripts prove unusable. It is paid and 2–120s only.
- A failed transcription (`TranscriptionStatus != completed`) is stored but not extracted — there
  is no text to work with.
- The four business metrics (D-022) are unchanged: voicemail jobs flow into `jobs`/capture rate,
  but `reply_rate` stays SMS-replies per text sent, so the frozen H6 measure is not diluted.

## Consequences

- `raw_events.source` gains `voicemail` (check constraint widened, migration 0009); the retry and
  90-day redaction queries now treat it like `sms_reply`.
- The TwiML is now built from `public_base_url` (the `transcribeCallback` needs an absolute URL
  Twilio can reach) rather than a module constant.

## Source

#33; founder decision 2026-11-14; D-021, D-022, D-024.
