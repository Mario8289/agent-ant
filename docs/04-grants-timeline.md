---
title: Grants & Free Tokens Timeline
status: draft
version: 0.4
last_updated: 2026-11-05
sources:
  - Vendor and programme pages, checked 2026-11-04 (links inline)
  - Microsoft Learn — Microsoft for Startups application process
  - AWS Startups — Activate Credits
  - Google Cloud — for Startups Cloud Program
  - Claude — Claude for Startups
  - Cloudflare — Workers AI pricing
  - Supabase — pricing page
  - GOV.UK — Sovereign AI
---

# 04 — Grants & Free Tokens Timeline

## Purpose

Sequence funding applications so credits arrive **before** they are needed, and competitive
cash grants are only attempted once there is evidence to show.

Figures below were checked against the vendor or programme page on **2026-11-04**. All of
these programmes change their terms; re-check the linked page before applying.

## Core distinction

**Grants are cash** and are taxed/accounted for differently from **credits**, which are
vouchers for a specific vendor's services. They are not interchangeable, and cash grants
usually carry reporting obligations.

## Timing principle

**Apply slightly before you need, not when you need.**

Review is usually days, not months: Microsoft reviews applications within three business
days, and AWS Activate decisions are typically 5–10 business days. The delay that actually
bites is eligibility, not review — most credit programmes require a registered company, a
company-domain email, and a live website. Those take longer to arrange than the application.

## Phase 1 — Now, before/during the precursor

**Prerequisites, in order:**

1. **A registered company.** Almost every credit programme below requires a legal entity and
   a website. Several also ask for a Companies House number.
2. **A company-domain email** (`you@yourdomain.co.uk`). Anthropic explicitly requires an email
   that matches the website domain; the same is standard elsewhere.
3. **A working website** with a clear description of the product.

| Programme | What it actually gives (checked 2026-11-04) | Gate | Use it? |
|---|---|---|---|
| [Microsoft for Startups Founders Hub](https://www.microsoft.com/en-us/startups) | $1,000 starter credits, scaling to $150,000; higher tiers are unlocked by usage and, for the top tiers, an Investor Network referral code | Business verification; no VC required for entry tiers | **Yes** — best bootstrapped ladder |
| [AWS Activate Founders](https://startups.aws.com/lp/aws-activate-credits) | $1,000, with selected startups eligible for up to $5,000 | Self-funded, pre-Series B, founded in the last 10 years, functioning website | **Yes** — Bedrock is the preferred LLM route (D-009), and the credits also cover the hosting account |
| [Google for Startups Cloud](https://cloud.google.com/startup) | Start tier $2,000 for one year; Scale tier up to $200,000; AI-first up to $350,000 | Start tier: founded in the last 2 years, working MVP, clear business model. Scale tiers require Pre-Seed–Series A funding | **Yes** — the $2,000 Start tier fits |
| [Claude for Startups](https://claude.com/programs/startups) | $1,000 Claude API credits, one year of Claude Team, partner offers (up to $45,000 combined value) | Company email on the website domain, Claude Console account, founded in the last 5 years. In practice API credits have gone to equity-funded startups, and the cohort has been capacity-limited | Apply, but do not plan around it |
| ~~Supabase startup credits~~ | **Programme discontinued** — `supabase.com/startups` returns 404 as of September 2026 | — | No. Use the free tier |
| [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/platform/pricing) | 10,000 Neurons/day free on both Free and Paid plans; $0.011 per 1,000 Neurons beyond that | None | Yes, if using Workers AI |

**Zero-cost dev tiers, no application:** Google AI Studio, Groq, Cerebras, Mistral free tier,
OpenRouter free models, GitHub Models, Cloudflare Workers AI, Supabase free tier (500 MB
database, 2 projects, pauses after 7 days of inactivity).

> ⚠️ **Data-protection caution:** free tiers commonly reserve the right to use inputs for
> training, and the terms differ by provider. **Do not send real customer names, phone numbers
> or job details to any free tier.** Use synthetic data during development, and move to a paid
> tier with a data-processing agreement before live customer data touches an LLM (risk R4,
> decision pending in issue #16).

## Phase 2 — During the sprint (Weeks 1–6)

- **Apply for nothing new.** Phase 1 credits should be landing.
- **Track spend weekly** so real burn is known by Week 6.
- Diary the expiry the day each credit lands. Microsoft credits in particular are time-boxed.

## Phase 3 — After the sprint (Week 7+), with evidence

| Programme | Reality check | Why wait |
|---|---|---|
| [Innovate UK Smart Grants](https://apply-for-innovation-funding.service.gov.uk/competition/search) | Single-company projects can request roughly £25,000–£500,000 at up to 70% of eligible costs; project sizes and bands change per round, so read the live competition | Competitive, needs a UK-registered company, match funding and a credible R&D project |
| [UK Sovereign AI Fund](https://www.gov.uk/government/news/ai-firms-pioneering-drug-discovery-cheaper-supercomputing-and-more-get-first-backing-through-uks-sovereign-ai) | £500m equity fund launched April 2026; investments around £1m–£10m per round, plus compute | Far too early, and it is equity, not a grant |
| Cloudflare (scaled) | Only relevant if traffic is real | — |

Applying for competitive cash grants pre-prototype wastes the attempt.

## Application order

1. Register the company and buy the domain + company email
2. Free dev tiers (today, no application, synthetic data only)
3. Microsoft Founders Hub (entry tier, no investor needed)
4. Google for Startups Start tier ($2,000)
5. AWS Activate Founders (Bedrock is the preferred LLM route, so this is now on the list)
6. Claude for Startups (capacity-limited; treat as upside)
7. Diary: revisit Innovate UK after Week 6

## Anti-patterns

- ⚠️ **Building the stack around whichever credit arrives first.** Credits expire; architecture
  decisions outlive them. Choose the stack on merit, use credits to offset cost.
- ⚠️ **Treating credits as revenue or validation.** A voucher is not a customer.
- ⚠️ **Chasing cash grants before evidence exists** — burns the one shot at a competitive round.
- ⚠️ **Letting credits lapse silently.** Diary the expiry the day the credit lands.
- ⚠️ **Assuming a programme still exists.** Supabase's startup programme is gone; several
  "startup credit" listicles still advertise it.

## Open questions

- Is incorporation required before the Microsoft and Google entry tiers? (Microsoft asks for
  business verification; Google asks for a working MVP.)
- Which provider wins the Week 4 DPA lock? Bedrock is the default; see
  [ADR 0002](./adr/0002-llm-provider.md) and issue #29.
- Does the £2,000 Google Start tier cover the Gemini API, or only Cloud/Firebase?

## Change history

- **0.4 (2026-11-05)** — AWS Activate promoted: Bedrock is the preferred LLM route (D-009), so
  the credits now cover both inference and hosting. DPA question moved to the Week 4 gate.
- **0.3 (2026-11-04)** — every figure re-checked against the programme page; Supabase startup
  credits marked discontinued; Anthropic terms and capacity caveat added; Innovate UK and
  Sovereign AI figures corrected; company/domain prerequisites made explicit.
- **0.2 (2026-11-04)** — whole document flagged unverified; free-tier data-protection caution
  added; phased timing retained; anti-patterns added.
- **0.1** — same programme list presented as established fact.
