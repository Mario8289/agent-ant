---
title: Mom Test Interview Script — Sole Traders
status: draft
version: 0.3
last_updated: 2026-11-17
sources:
  - Fitzpatrick — The Mom Test (2013) — verified
---

# 02 — Mom Test Interview Script

## Purpose

Learn how a tradesperson **actually** runs the business side of the work — calls, quotes,
invoices, receipts and year-end paperwork — without revealing the product idea. Feeds **H1**,
**H3**, **H7** and **H9** in [01-hypothesis-table.md](./01-hypothesis-table.md). Record each
interview in [03-requirements-capture-sheet.md](./03-requirements-capture-sheet.md).

**Printable copy:** [print/interview-script.html](./print/interview-script.html) (and the PDF
next to it). Regenerate the PDF with `just print-script` after editing either file.

**Setting:** casual, over a cuppa. Not a "meeting".
**Duration:** 30–40 minutes. Take notes; record only if they are comfortable.

## The three rules (Fitzpatrick)

1. Talk about **their life**, not your idea.
2. Ask about **specifics in the past**, not generics or future opinions.
3. **Talk less, listen more** — aim to speak ~20% of the time.

## Before you start

- **Do not mention the app.** Not once, including at the end. Interview 1 drifted into a
  pitch in the second half, and every positive reaction after that point is unusable.
- **No prices.** Never ask "would you pay £20 / £50". Commitment is asked for, not polled.
- **Wait 3 seconds** after each answer. The useful detail often comes after the pause.
- **Chase specifics.** "Yeah, I miss calls sometimes" → "When was the last time? What happened?"
- **Do not pitch, defend, or suggest.** If they complain, say "tell me more", not "I could fix that".
- **Pick a quiet room.** Background conversation made parts of interview 1 hard to transcribe.

> ⚠️ **Anti-pattern (Fitzpatrick): pitching during discovery.** It contaminates every answer
> that follows. "Compliments are the fool's gold of customer learning: shiny, distracting,
> and worthless" (verified).

## Opening (no pitch)

> "I'm trying to get my head round how people in the trade actually run the business side of
> things — the calls, the quotes, the invoices, the paperwork. Not the work itself. Can I ask
> you a few things about how it really works for you? No agenda, I'm just curious."

Then stop talking.

## Section 0 — Who they are (segment)

Interview 1 showed the answer to Section A depends on where the work comes from. A trader
whose income is subcontract work can shrug off missed private enquiries; one who lives on
them cannot.

1. Roughly how much of your work comes from private customers, and how much through a
   company or main contractor?
2. Where did your last three jobs come from?
3. How long have you been trading on your own? Anyone helping with the books?

## Section 1 — The admin, unprompted (H1, H9)

Ask this **before** any topic-specific section so the answer is not led.

4. What's the most boring or frustrating part of the business side for you?
5. What else? *(get three, in their words)*
6. When did you last spend time on that? What were you doing?

## Section A — The missed call (H1, G0b)

7. Walk me through what happens when the phone rings while you're up a ladder or mid-job.
8. When was the last time you missed a call from a customer? What happened next?
9. What did you do — ring back, text, nothing?
10. Did that one turn into a job, or did you lose it?
11. How often in a normal week? *(then: what happened last week specifically?)*
12. When you lose a job that way, what does it cost you, roughly?
13. Last time you rang a tradesperson and got a text back instead of an answer, what did you
    do? *(G0b — behaviour, not opinion)*

**Listen for:** real examples, real numbers. "I don't ring them back" is an answer: ask why,
and whether that work matters to them.

## Section B — Enquiries and quotes

14. Talk me through a new customer from first contact to starting the job.
15. How do you do quotes now — pen and paper, phone, computer?
16. Where do you get material prices when pricing a job?
17. How long did your last quote take, start to finish? When did you do it?

## Section C — Invoices and getting paid (H4)

18. How do you do invoices — who, how, when?
19. When was the last time someone was late paying? What did you do?
20. How much are you owed right now?

## Section D — Receipts, job costs and year-end (H9)

21. Where do the receipts for a job go while it's running?
22. Walk me through the last job you totalled up. How long did it take?
23. When did you last lose a receipt? What happened?
24. Supplier invoices that come by email — what happens to them?
25. Walk me through getting your year-end paperwork ready. How long did it take last year?
26. Who does your accounts? What do you hand them, and what do you still do yourself?
27. What does that cost you?

**Listen for:** hours, lost receipts, evenings and weekends. Ask to **see** a real job's
paperwork if they have it to hand — that beats any description.

## Section E — What they have already tried

Fitzpatrick's "what else have you tried?" separates real pain from idle wishing.

28. Have you ever tried any software or an app for any of this?
29. What happened — stuck with it or binned it? Why?
30. What do you use your phone for, business-wise, day to day?
31. Who else in the trade has this sorted? What do they do?

**Listen for:** actively tried to solve it (strong signal) vs. never bothered (weak signal).

## Section F — Commitment ask (H3, H7)

Real signal is commitment in one of three currencies: **time, reputation, cash**.

| Currency | Ask | Strength |
|---|---|---|
| Time | "Could I sit with you next time you total up a job and watch how you do it?" | weakest |
| Reputation | "Know one or two others in the trade I could have the same chat with? Could you intro me?" | medium |
| Cash | Only once something exists: a small deposit or pre-order. Never a hypothetical price. | strongest |

**Reading the answer:**
- "Yeah, sounds good, let me know" → **politeness, means nothing.**
- Actually books a time / makes an intro / pays a deposit → **real signal.**

## Never ask (Fitzpatrick)

- ❌ "Do you think this is a good idea?"
- ❌ "Would you use an app that does X?"
- ❌ "How much would you pay for something like this?" — including "would £20 a month be OK?"
- ❌ "What would your dream app do?"
- ❌ "Don't you find it annoying when…?" *(leading — puts words in their mouth)*

## After the interview — capture within an hour

Fill the person's column in [03-requirements-capture-sheet.md](./03-requirements-capture-sheet.md).
No names, phone numbers or third-party names in the repo; keep recordings and transcripts out
of git.

## Judging the result

- **Strong:** specific past events, names a lost job or a lost receipt, gives time or an intro.
- **Weak:** "yeah it happens", no examples, polite encouragement.
- **Gate G0a:** if fewer than 3 of 6 recall a **specific** missed call **and** a lost job,
  do not build the missed-call wedge.

## Interviewing your dad specifically

He will want to be encouraging. Manage that bias actively:

1. **Give permission to be negative:** "I need you to be brutally honest, even if it means
   telling me it's a rubbish idea. That's genuinely more helpful."
2. **Watch behaviour, not words.** If something is a big problem but he has never once
   tried to fix it, believe the behaviour. Past actions over stated opinions.

## Open questions

- Will a trader tolerate a fixed-template SMS going to their customers under their name?
  Question 13 asks it as past behaviour; the answer still needs a live test (H6).

## Change history

- **0.3 (2026-11-17)** — generalised from Dad to all six interviewees (file renamed from
  `02-mom-test-script-dad.md`). Added Section 0 (private vs subcontract work), an unprompted
  admin-pain section, Section D on receipts and year-end paperwork (H9), and a behavioural
  G0b question. Removed pricing polls and the "rough idea" demo ask after interview 1.
  Printable copy added.
- **0.2 (2026-11-04)** — attribution made explicit; anti-pattern callout added; commitment
  table added; linked to hypotheses H1/H3/H7 and gate G0a/G0b.
- **0.1** — initial script, same questions, looser sourcing.
