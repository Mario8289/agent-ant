---
title: Competitor Gap Analysis
status: draft
version: 0.1
last_updated: 2026-11-22
sources:
  - Powered Now pricing page, fetched 2026-11-22 (powerednow.com/pricing) — vendor page, verified
  - Tradify UK pricing page, fetched 2026-11-22 (tradifyhq.com/uk/pricing) — vendor page, verified
  - Fergus pricing page, fetched 2026-11-22 (fergus.com/pricing) — shows AU/NZ pricing, not UK
  - Traddie pricing page, fetched 2026-11-22 (gettraddie.com/pricing) — vendor page, verified
  - Dext price from a third-party roundup (theselfemployedclub.com, 2026-11-04) — not a vendor page, unverified
  - VioTrade — not re-checked. viotrade.com now redirects to a domain-for-sale page
  - Web search 2026-11-22 — mostly vendor and affiliate marketing, treated as unverified
---

# Competitor Gap Analysis

## Purpose

Say where existing tools overlap with what we plan to build (receipt capture, job spend against
quote, chasing, call answering) and where we could stand out. It feeds the positioning in D-033
and extends the competitor tables in [roadmap §1](./roadmap.md) and [business plan §3](./business-plan.md).

**Scope of the claim.** This reads vendor pricing and feature pages only. Nobody on this list has
been trialled yet. A "gap" below means *not advertised*, not *proven absent*. The spike
([#151](https://github.com/Mario8289/agent-ant/issues/151)) closes that by trialling the products.

## 1. What the vendors say (fetched 2026-11-22)

Prices are list prices per month, ex VAT unless the vendor says otherwise.

| Product | Entry plan | Mid / top plan | AI receipt scanner | Auto-chasing | Metered or add-on extras |
|---|---|---|---|---|---|
| **Powered Now** | Business £28, one user. Expenses, supplier invoices, purchase orders, MTD | Professional £32 per user, Premium £40 per user | Premium only (£40) | Premium only (£40) | PN Receptionist £29 (speech) or £39 (speech and text). Here Is My Work Premium £100 a year |
| **Tradify** | Lite £34 per user | Pro £37, Plus £44 per user | Plus only (£44): "SmartRead for Bills" | Pro (£37): quote and invoice reminders | Text messages £0.10 each. Instant Website £10 a month |
| **Fergus** | Basic from $53 | Pro from $75 | Not on the pricing page | Not on the pricing page | SMS $15 per 100 texts, certificates $30, card payments 2.95% + $0.30. Page shows AU/NZ pricing. UK figures of £39 and £45 appear in a third-party source only |
| **Traddie** | Solo £9.99. Tracks expenses and receipts | Pro £19.99, Team £49.99 | Pro (£19.99): unlimited receipt scanning | Pro (£19.99): automatic payment reminders | Extra users £7 each |
| **Dext** | About £24 a month (£290 a year + VAT), per a third-party source | — | Core product | — | Receipts only. Sends to Xero, QuickBooks or Sage |
| **VioTrade** | £20 a month per the repo (roadmap §1) | — | "Bundled extras" per the repo | Overdue-payment texts per the repo | Not re-checked |

**What a sole trader pays to get AI receipts, chasing and call answering together.** Powered Now:
Premium £40 plus Receptionist with texts £39 is **£79 a month**. Tradify: Plus £44, plus £0.10 per
text. Traddie is the exception: Pro at £19.99 includes scanning and reminders. Price alone will not
differentiate us against Traddie.

## 2. Gaps (not advertised, unverified)

1. **Capture is form-based everywhere.** Receipt capture means opening the app, taking a photo and
   picking a job. We saw nothing about capture by sending a photo to a messaging number.
2. **AI is added to the top tier.** It appears as scanning, writing help and rule-based reminders.
   We saw no assistant that does a task and asks for approval.
3. **Bundles are wide.** Certificates, timesheets, team scheduling, VAT returns and card payments
   drive the price and complexity. A sole trader may use few of them.
4. **Messaging is metered.** Texts are charged per message (Tradify £0.10, Fergus $0.15) or sold as
   a Receptionist upgrade.
5. **Spend against quote is a paid-tier "job costing" feature.** Tradify Pro, Fergus Pro, and Powered
   Now at a higher tier than Business.

## 3. Where we could stand out (hypotheses)

- **Chat is the interface.** Send a receipt photo, ask "how's the Patel job?", get the answer in the
  thread. Tested by H9 and by whether the trader uses chat over forms.
- **One plan with AI and messaging included.** No add-ons, no per-text charges. The price is not set.
  It waits on the pricing conversation (#36).
- **Deliberately small.** Receipts, job spend against quote, missed calls, leads. No certificates,
  timesheets, scheduling, VAT returns or card payments. Export CSV and hand off to accounting tools.
- **Proactive.** The assistant flags a job nearing its quote instead of waiting to be opened.

## 4. Risks

- Incumbents are already adding AI. Powered Now has an AI receipt scanner and an AI receptionist. A
  chat front end is a small step for them.
- Traddie undercuts every other tool on price and already scans receipts.
- "Chat-first suits the trader" rests on interview 1 only (Dad dislikes business apps). It is a
  hypothesis until the other interviews say so.
- Dext and Fergus UK pricing, and the VioTrade figure, are not verified.

## 5. Not done yet

- Trial Powered Now, Tradify and Traddie. Capture their receipt and job-costing flows.
- Confirm VioTrade's current domain and pricing; verify Dext on its own site.
- Check for chat or WhatsApp capture in any of these products, not only their pricing pages.

## Changelog

- **0.1 (2026-11-22)** — first draft from vendor pricing pages and one web search.
