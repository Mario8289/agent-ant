---
title: Agent Roadmap
status: draft
version: 0.1
last_updated: 2026-11-14
sources:
  - Thiel — Zero to One (2014) — 10x on one axis, escape competition — verified (doc 00)
  - Ries — The Lean Startup (2011) — validated learning, commit pass lines first — verified (doc 00)
  - Fitzpatrick — The Mom Test (2013) — past behaviour over opinions — verified (doc 00)
  - Competitor pages fetched 2026-11-14 — VioTrade, Jobber AI, Sintra (see Sources)
  - Web search 2026-11-14 — mostly vendor marketing, treated as unverified (see Sources)
---

# 12 — Agent Roadmap

## Purpose

Rank the agents that could follow `missed_call`, say what each one does, and group them into
roles a tradesperson recognises. The product idea is that a sole trader should feel they have
the back office of a much larger firm: a secretary, an estimator, an accounts clerk.

This is a **plan, not a build order that has started**. Per D-030, no code for any agent here
is written until the missed-call prototype is finished and its gates have passed.

> ⚠️ **The ranking is a desk judgement.** The discovery sheet
> ([03](./03-requirements-capture-sheet.md)) was empty when this was written. H4 is tested by
> what Dad asks for next, unprompted. His answer overrides this order.

## 1. What competitors already cover

Checked 2026-11-14. Extends the pricing table in [00 §3](./00-business-plan.md).

| Layer | Who does it | Read |
|---|---|---|
| Call answering, text-back | Clara, Rosie, Down To Earth AI, Powered Now Receptionist (launched Sept 2026, from £29/mo per its own site), Jobber, ServiceM8, FieldCamp | Commodity. Do not invest further here |
| Quotes, invoices, jobs, CRM | VioTrade (£20/mo, all-in), Tradify, Fergus, Jobber, ServiceM8 | Covered, but generic across trades and mostly forms the trader fills in |
| Follow-ups and chasing | Tradehand, Jobber Automations, VioTrade (overdue-payment texts) | Present but shallow |
| "AI employees" by role | Sintra (12 named roles), Marblism, GoHighLevel AI Employee | Same role framing, but horizontal and content-led. No trade job data behind it |
| Receipts, VAT, Xero sync, RAMS | VioTrade | Bundled extras |

**Gap:** nobody combines the role framing with deep trade data. That matches the conclusion in
doc 00 that the differentiation is what happens *after* the call.

**Not checked:** Tradehand's site returned HTTP 403, so its row relies on doc 00. Prices were
not re-verified beyond the pages listed under Sources.

## 2. The standout capability (candidate answer to H5)

**Quotes priced the way the trader prices.** The quote drafter learns from the trader's own
past quotes and what jobs actually cost him. A missed call at 2pm becomes a draft quote in his
rates, waiting for a one-tap approval that evening.

- **Why it stands out.** VioTrade and Jobber both draft quotes, but from generic estimating or
  a catalogue the trader maintains. The role-based tools have no job data at all. None of the
  sources showed a product going from enquiry to a priced quote in the trader's own numbers.
- **Why it compounds.** Every approved or edited quote improves the next one. That history
  cannot be copied by a £20/mo all-in-one, and it feeds the later agents (materials, margin
  reporting, invoices).
- **What is not known.** Whether Dad has past quotes in a usable form (paper, texts, memory),
  and whether slow quoting actually loses him jobs. The two quoting rows in doc 03 answer
  both, and both are blank. If he prices from memory, the cold start is hard and this weakens.

This is a hypothesis for [issue #15](https://github.com/Mario8289/agent-ant/issues/15)
(10x axis), not a finding.

## 3. Agents in order of importance

Ranked on four things: closeness to money, reuse of what `missed_call` already produces,
compliance exposure, and how well competitors already do it.

| # | Agent | Capabilities | Why this rank |
|---|---|---|---|
| 1 | **Quote drafter** | Job record → draft quote with line items, materials, labour and margin. Trader edits and approves. Learns from his past quotes | The 10x candidate (§2). Reuses the job record |
| 2 | **Follow-up chaser** | Nudges callers who never replied to the auto-text. Chases sent quotes at set intervals. Flags leads going cold | Cheapest to build on the existing SMS, retry and template plumbing. Lifts capture directly |
| 3 | **Booking and diary** | Offers survey or job slots, writes to the calendar, sends reminders, handles reschedules | Closes the loop from enquiry to booked job, the money metric |
| 4 | **Invoice and payment chaser** | Approved job or quote → invoice. Polite, escalating reminders. "Who owes me" list | Hiscox: 19% of payments to sole traders are late. The H4 adjacency, deferred by doc 00 until trust is earned |
| 5 | **Multi-channel inbox** | Email, web form, Facebook and Checkatrade enquiries into the same extraction pipeline and job record | High reuse. WhatsApp is the awkward one (needs the Business API) |
| 6 | **Reviews and reputation** | Review request after a paid job. Drafts replies to Google reviews for approval | Small build, visible value, feeds marketing |
| 7 | **Bookkeeper** | Receipt photo → expense. Job-level profit. Quarterly pack exported to Xero, Sage or FreeAgent | Making Tax Digital is a tailwind, but crowded and compliance-heavy. Integrate, do not become the tax software |
| 8 | **Marketing content** | Job photos → portfolio and social posts. Google Business Profile updates. Past-customer reactivation | Horizontal tools do this generically; ours would use real job data. Reactivation needs marketing consent |
| 9 | **Materials and procurement** | Quote → materials list. Merchant price comparison. Purchase orders | Deepens the quoting moat. Depends on #1 and on supplier price data |
| 10 | **Compliance and paperwork** | RAMS, insurance and certification renewal reminders, standard terms | Needed occasionally. VioTrade already bundles RAMS |
| 11 | **Business analyst** | Weekly digest: win rate, margin by job type, lead sources, cash due | Only useful once agents 1–4 generate data |
| 12 | **Live voice receptionist** | Answers calls in real time | Last on purpose: the most crowded layer and the highest risk (D-002) |

## 4. Roles

A role is what the trader sees. An agent is what we build. One role can hold several agents.

| Role | Agents |
|---|---|
| Secretary / receptionist | Missed call (built), multi-channel inbox, booking and diary, live voice |
| Estimator | Quote drafter, materials and procurement |
| Sales coordinator | Follow-up chaser |
| Accounts clerk | Invoice and payment chaser, bookkeeper |
| Marketing manager | Reviews and reputation, marketing content |
| Compliance officer | Compliance and paperwork |
| Business manager | Business analyst |

Role names are placeholders for the founder to settle. They are presentation only and do not
change the package layout (`agents/<name>`, one package per agent).

## 5. What is planned now, and what blocks it

Epics and stories are written for **agents 1–4 only**. Agents 5–12 stay as rows in §3 until
the first four have taught us something; stories for them now would be guesses.

| # | Agent | Epic | Stories |
|---|---|---|---|
| 1 | Quote drafter | [#103](https://github.com/Mario8289/agent-ant/issues/103) | #104–#109 |
| 2 | Follow-up chaser | [#110](https://github.com/Mario8289/agent-ant/issues/110) | #111–#114 |
| 3 | Booking and diary | [#115](https://github.com/Mario8289/agent-ant/issues/115) | #116–#120 |
| 4 | Invoice and payment chaser | [#132](https://github.com/Mario8289/agent-ant/issues/132) | #133–#137 |

All sit under the `Post-W6 roadmap` milestone.

Every epic and story carries the `blocked-by-gate` label and is blocked by:

| Blocker | Issue |
|---|---|
| The missed-call prototype is finished | [#3](https://github.com/Mario8289/agent-ant/issues/3) |
| G0a discovery: ≥3 of 6 cite a specific missed call and a lost job | [#10](https://github.com/Mario8289/agent-ant/issues/10) |
| Week 4 gate: Dad approves or corrects ≥1 real job unaided (H2) | [#32](https://github.com/Mario8289/agent-ant/issues/32) |
| Week 6 continue/kill review | [#37](https://github.com/Mario8289/agent-ant/issues/37) |

The quote drafter is also blocked by the 10x-axis decision
([#15](https://github.com/Mario8289/agent-ant/issues/15)).

A failed G0a still means stop. In that case these epics are closed as Won't Do, not started.

## 6. Rules every new agent inherits

The non-negotiable rules in `AGENTS.md` apply unchanged. Three matter most here:

- **No free-text from the AI to customers (D-004).** Quotes, invoices, nudges and reminders
  reach the customer only as fixed templates filled with structured, trader-approved fields.
- **Human approval before anything is confirmed or sent.** A draft quote, a booking and an
  invoice all wait for the trader.
- **Trusted fields never come from the LLM.** Prices on a sent quote or invoice are the values
  the trader approved, never a model output passed straight through.

## Anti-patterns

- ⚠️ **Building agent 2 because the plan exists.** The plan is cheap; the gates are the test.
- ⚠️ **"VioTrade plus one more feature"** (Thiel, doc 00). Twelve shallow agents is that
  mistake at scale. Depth on quoting first.
- ⚠️ **Treating this ranking as evidence.** It is a desk ranking. Interviews outrank it.
- ⚠️ **Letting the chaser dilute the frozen metrics.** Replies won by a nudge are reported
  separately from `reply_rate` (D-022), or H6 can no longer be read.

## Open questions

- **How does D-004 apply to quotes?** A quote is customer-facing text. Proposed: the model
  fills structured line items into a fixed template and the trader approves; no model prose
  reaches the customer. Owner: founder. Gates the quote drafter's send story.
- **Does Dad have past quotes in a usable form?** Owner: founder, via doc 03. Decides whether
  §2 survives.
- **Which agent does Dad ask for, unprompted (H4)?** Owner: founder, Week 6 write-up. Can
  reorder §3.
- **Role names.** Owner: founder.

## Sources

Fetched or searched 2026-11-14. Vendor pages describe their own products; treat claims as
unverified.

- [VioTrade](https://viotrade.co.uk) — feature list and pricing
- [Jobber AI features](https://www.getjobber.com/features/ai/)
- [Sintra: best AI employees](https://sintra.ai/blog/best-ai-employees) — role roster, other platforms
- [Powered Now Receptionist](https://powerednow.com/receptionist/)
- [FieldCamp AI receptionist](https://fieldcamp.ai/uk/ai-receptionist.md)
- [HighLevel AI Employee announcement](https://www.newswire.com/news/highlevel-unveils-new-ai-employee-to-revolutionize-business-automation-22467082)
- [Hiscox late payments report, via ByteStart](https://www.bytestart.co.uk/news-insights/uk-small-businesses-still-owed-70bn-in-late-payments-says-hiscox-report/)
- [Tide: Making Tax Digital admin](https://www.tide.co/blog/tide-update/making-tax-digital-admin/)

## Change history

- **0.1 (2026-11-14)** — created: competitor coverage, 12 ranked agents, role grouping, the
  quoting hypothesis for H5, and the blocking rule (D-030).
