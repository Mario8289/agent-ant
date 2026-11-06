---
title: Telephony Forwarding Test (G0b runbook)
status: draft
version: 0.1
last_updated: 2026-11-06
sources:
  - Apple Support — "Set up call forwarding on iPhone" (checked 2026-11-06)
  - Twilio docs — "Respond to Incoming Phone Calls" (checked 2026-11-06)
---

# 08 — Telephony Forwarding Test (G0b runbook)

## Purpose

Gate **G0b** asks one question: when Dad's phone is not answered, does the call forward to a
Twilio number with the caller's number intact? If not, the telephony design changes before any
code is written (see [00 §6](./00-business-plan.md) and issue [#11](https://github.com/Mario8289/agent-ant/issues/11)).

This runbook is the step-by-step test. Results go on #11.

## What is being tested

| Piece | Where it is set | Test |
|---|---|---|
| Twilio number receives calls | Twilio console → number → Voice Configuration | Call it directly and hear the test message |
| Call handler | "A call comes in" set to the TwiML Bin `forwarding-test` | Message plays |
| No-answer forwarding | The phone's own settings or dial codes, **not** Twilio | Let the phone ring out; the call reaches Twilio |
| Caller ID preserved | Twilio call log, field **From** | From shows the caller, not Twilio |

## Step 1 — Twilio side (done once)

1. Confirm **+44 753 302 1710** is active under Phone Numbers.
2. Confirm the TwiML Bin `forwarding-test` exists:
   ```xml
   <Response>
     <Say>Forwarding test received. Goodbye.</Say>
   </Response>
   ```
3. On the number's Configure page, set **A call comes in** to **TwiML Bin** → `forwarding-test`, then **Save configuration**.
4. Call the number from another phone. You should hear the message.

## Step 2 — Set no-answer forwarding on the test phone

The iPhone's built-in **Call Forwarding** setting (Settings → Apps → Phone → Call Forwarding) only
forwards **every** call. It cannot forward only when the phone is unanswered. Apple's own
page says conditional forwarding must be set up with the carrier.

For no-answer forwarding, dial the GSM codes in the Phone app. These are the standard codes;
confirm they work on your network before relying on them.

| Action | Dial | Notes |
|---|---|---|
| Forward when not answered | `**61*+447533021710#` then call | Forward after the default ring time |
| Set the ring time | `**61*+447533021710**20#` | Seconds: 5, 10, 15, 20, 25 or 30. Here 20 seconds |
| Check the status | `*#61#` then call | Shows where no-answer calls go |
| Turn off no-answer forwarding | `##61#` then call | Do this after the test |

If the carrier rejects a code, check their support page for "conditional call forwarding" and
record the code they give you on #11.

**Earlier draft error:** a ring-time form with `*11*` was wrong. Use `**61*number**seconds#`.

## Step 3 — Run the test

1. Activate no-answer forwarding on the test phone.
2. From a **different** phone, call the test phone and do not answer.
3. After the ring time, the caller should hear "Forwarding test received. Goodbye."
4. Check the log: **Monitor → Logs → Calls** in Twilio. The forwarded call should show the
   caller's number in **From**.
5. Turn off forwarding with `##61#`.

## Step 4 — Dad's phone (only after step 3 passes)

Repeat with Dad's handset, using his carrier's code. Do not use his phone for the first test.

## Pass and fail

| Result | Meaning |
|---|---|
| Forward triggers, From is the caller's number | G0b passes for this network |
| Forward triggers, From is Twilio's number | Caller ID is lost. Telephony design changes before code |
| Forward never triggers | Carrier code or network issue. Try the carrier's code, then escalate |
| Works on one network only | Record which networks pass; the MVP may need to support only those |

## Record on #11

- Carrier and network (for example EE, O2, Vodafone, Three, or a mobile virtual network)
- Exact codes used and whether they were accepted
- Ring time set
- Whether the forward triggered
- What the **From** field showed
- Any delay or error

## Change history

- **0.1 (2026-11-06)** — first version, written after testing the iPhone setting. Corrects the
  ring-time code and records that the built-in iPhone setting is unconditional only.
