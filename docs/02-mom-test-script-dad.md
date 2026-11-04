---
title: Mom Test Interview Script — Dad (Carpenter, 60)
status: draft
version: 0.2
last_updated: 2026-11-04
sources:
  - Fitzpatrick — The Mom Test (2013) — verified
---

# 02 — Mom Test Interview Script — Dad

## Purpose

Learn how Dad **actually** runs the business side of carpentry — missed calls, quotes,
invoices — without revealing the product idea. Feeds **H1**, **H3**, **H7** in
[01-hypothesis-table.md](./01-hypothesis-table.md).

**Setting:** casual, over a cuppa. Not a "meeting".
**Duration:** 30–40 minutes. Take notes; record only if he is comfortable.

## The three rules (Fitzpatrick)

1. Talk about **his life**, not your idea.
2. Ask about **specifics in the past**, not generics or future opinions.
3. **Talk less, listen more** — aim to speak ~20% of the time.

## Before you start

- **Do not mention the app.** Not once. The moment he knows you are building something he
  will try to be helpful and tell you what you want to hear.
- **Wait 3 seconds** after each answer. The useful detail often comes after the pause.
- **Chase specifics.** "Yeah, I miss calls sometimes" → "When was the last time? What happened?"
- **Do not pitch, defend, or suggest.** If he complains, say "tell me more", not "I could fix that".

> ⚠️ **Anti-pattern (Fitzpatrick): pitching during discovery.** It contaminates every answer
> that follows. "Compliments are the fool's gold of customer learning: shiny, distracting,
> and worthless" (verified).

## Opening (no pitch)

> "Dad, I'm trying to get my head round how blokes like you actually run the business side of
> things — the calls, the quotes, the invoices, all that. Not the woodwork, the paperwork.
> Can I just ask you a few things about how it really works for you? No agenda, I'm just curious."

Then stop talking.

## Section A — The missed call (H1)

1. Walk me through what happens when the phone rings while you're up a ladder or mid-job.
2. When was the last time you missed a call from a customer? What happened next?
3. What did you do — ring back, text, nothing?
4. Did that one turn into a job, or did you lose it?
5. How often in a normal week? *(then: what happened last week specifically?)*
6. When you lose a job that way, what does it cost you, roughly?

**Listen for:** real examples, real numbers. If he cannot recall a specific instance, the pain
may be weaker than assumed — that is important to know.

## Section B — Enquiries and quotes

7. Talk me through a new customer from first contact to starting the job.
8. How do you do quotes now — pen and paper, phone, computer?
9. Where do you get material prices when pricing a job?
10. How long does a quote take? Walk me through the last one.

## Section C — Invoices and getting paid (feeds H4)

11. How do you do invoices — who, how, when?
12. When was the last time someone was late paying? What did you do?
13. How do you chase someone who hasn't paid? Walk me through it.
14. Does chasing money bother you — is it something you put off?
15. How much would you say you're owed right now in late invoices?

## Section D — What he has already tried

Fitzpatrick's "what else have you tried?" separates real pain from idle wishing.

16. Have you ever tried any software or an app for any of this?
17. What happened — stuck with it or binned it? Why?
18. What do you use your phone for, business-wise, day to day?
19. Who else in the trade has this sorted? What do they do?

**Listen for:** actively tried to solve it (strong signal) vs. never bothered (weak signal).

## Section E — Commitment ask (H3, H7)

Real signal is commitment in one of three currencies: **time, reputation, cash**.
Pick one, start gentle.

| Currency | Ask | Strength |
|---|---|---|
| Time | "Up for me showing you a rough idea in a couple of weeks for your honest take?" | weakest |
| Reputation | "Know one or two other carpenters I could have the same chat with? Could you intro me?" | medium |
| Cash | "If I built something that sorted the missed-call thing, would you pay a few quid a month?" — better: a small deposit once something exists | strongest |

**Reading the answer:**
- "Yeah, sounds good, let me know" → **politeness, means nothing.**
- Actually books a time / makes an intro / pays a deposit → **real signal.**

## Never ask (Fitzpatrick)

- ❌ "Do you think this is a good idea?"
- ❌ "Would you use an app that does X?"
- ❌ "How much would you pay for something like this?"
- ❌ "What would your dream app do?"
- ❌ "Don't you find it annoying when…?" *(leading — puts words in his mouth)*

## After the interview — capture within an hour

Transfer to [03-requirements-capture-sheet.md](./03-requirements-capture-sheet.md).

| Field | Notes |
|---|---|
| Missed calls per week (actual) | |
| Last missed call — what happened | |
| Jobs lost that way (recent) | |
| Estimated value lost | |
| Current tools / apps | |
| Tried a fix before? Stuck or binned? | |
| Invoice process | |
| Last late payment — what happened | |
| How he chases money | |
| Top 3 admin pains (his words) | |
| Commitment given (time / reputation / cash / none) | |
| Verbatim quotes | |

## Judging the result

- **Strong:** specific missed calls, names a lost job, gives time or an intro.
- **Weak:** "yeah it happens", no examples, polite encouragement.
- **Gate G0a:** if fewer than 3 of 6 interviewees confirm missed calls as a top-3 pain
  **with a real past example**, do not build.

## Interviewing your dad specifically

He will want to be encouraging. Manage that bias actively:

1. **Give permission to be negative:** "I need you to be brutally honest, even if it means
   telling me it's a rubbish idea. That's genuinely more helpful."
2. **Watch behaviour, not words.** If missed calls are a big problem but he has never once
   tried to fix it, believe the behaviour. Past actions over stated opinions.

## Open questions

- Does he agree to forward unanswered calls to a Twilio number? (Needed for gate G0b.)
- Will he tolerate a fixed-template SMS going to his customers under his name?

## Change history

- **0.2 (2026-11-04)** — attribution made explicit; anti-pattern callout added; commitment
  table added; linked to hypotheses H1/H3/H7 and gate G0a/G0b.
- **0.1** — initial script, same questions, looser sourcing.
