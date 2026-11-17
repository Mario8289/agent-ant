---
id: D-010
title: "Start Week 1 build before G0a, G0b and the beachhead decision"
status: accepted
date: 2026-11-07
---

# D-010 — Start Week 1 build before G0a, G0b and the beachhead decision

- **Date:** 2026-11-07
- **Status:** accepted
- **Reversible?** cheap — about one week of segment-agnostic plumbing.

## Context

The plan says build work waits for the pre-sprint gates: G0a (6 Mom Test
interviews, #10), G0b (forwarding on Dad's real plan, #47) and the beachhead decision (#15).
None are done. G0c's spikes are built (#59, #60, #61, PR #65 pending merge). The founder wants to start coding and
will do the interviews and the questionnaire later.

## Decision

Start Week 1 (#19, #18, #20, #21) now. Until #15 is decided, the working
assumption is **tradespeople in general** (carpenters, plumbers and similar), not one trade.
The gates are deferred, not dropped.

## Consequences

Week 1 is persist-raw-event, signature-verified webhook, fixed-template SMS
and reply storage. None of it depends on the segment, so little is lost if the segment
changes. The risk carried: if G0a fails or G0b fails, Week 1 effort is wasted and the
telephony design may have to change. Deferral does not lift the other rules: no real customer
data before #16, nothing reaches a real customer before the Week 4 gates, and a failed G0a
still means stop and reconsider the wedge (business plan §6).

## Source

founder decision, 2026-11-07; [business plan](../product/business-plan.md) §6
