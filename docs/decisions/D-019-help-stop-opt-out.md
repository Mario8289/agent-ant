---
id: D-019
title: "HELP/STOP opt-out: handle ourselves, confirm STOP and reply HELP (fixed templates)"
status: accepted
date: 2026-11-13
---

# D-019 — HELP/STOP opt-out: handle ourselves, confirm STOP and reply HELP (fixed templates)

- **Date:** 2026-11-13
- **Status:** accepted
- **Reversible?** cheap — delete a table and two webhook branches. Re-adopting Twilio Advanced
  Opt-Out later is possible but moves state out of Postgres.

## Context

Twilio's GB SMS guidance expects `HELP`/`STOP` support. The fixed missed-call
template (D-004) had neither, so a caller had no documented way to opt out; #72 tracked it. The
repo sends from a Twilio UK long code, which Twilio's free opt-out handling does not cover, so
the real choice was self-handle versus Twilio's paid Advanced Opt-Out.

## Decision

- **Handle opt-out ourselves**, not Twilio Advanced Opt-Out: one service, one Postgres (D-005),
  the state stays visible, and no per-number add-on cost. An `opt_outs` table keyed on
  `caller_number` records the opt-out; a caller is matched on the exact normalised body.
- **Confirm STOP and answer HELP**, each with a fixed one-line template (D-004: the AI never
  writes free text). STOP confirms the opt-out; HELP repeats the "reply with name / job /
  where" instruction.
- **Opt-out suppresses the auto-text, never the record.** A missed call from an opted-out number
  is still stored in `raw_events`, so the tradesperson sees it and can ring back; no lead is
  silently lost. Suppression applies only to the SMS.
- Keywords: `STOP`, `STOPALL`, `UNSUBSCRIBE`, `CANCEL`, `END`, `QUIT` opt out; `HELP` asks for
  help. Matching is case- and whitespace-insensitive, and only the exact keyword matches, so a
  normal reply like "help fix the tap" is untouched.

## Consequences

- `sms_reply` handles STOP/HELP before extraction, so they never reach the LLM or produce a job
  row. A STOP records the opt-out idempotently; a duplicate delivery confirms nothing twice.
- `missed_call` checks `opt_outs` before scheduling the text.
- New migration `0005` (`opt_outs`), a `db/opt_out.py` module, and tests covering idempotency,
  the STOP/HELP templates, and the "no second auto-text after STOP" guarantee.

## Source

Founder decision, 2026-11-13; Twilio GB SMS guidelines; D-004, D-005.
