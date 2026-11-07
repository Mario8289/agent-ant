---
title: Manual Steps — things only you can do
status: draft
version: 0.2
last_updated: 2026-11-07
---

# 10 — Manual Steps

Things the code cannot do for itself: console clicks, accounts, real phones. Each entry says
what blocks on it. Add to this list as steps come up; tick them off here when done.

## Open

### Point the Twilio number at the missed-call webhook
Blocks: a real forwarded call reaching the app (#18). The endpoint is built and tested, but
Twilio is not told about it yet.

1. Put the Twilio auth token in `.env` as `TWILIO_AUTH_TOKEN`. Without it the endpoint refuses
   every request (503) by design.
2. Run the app (`just dev`, port 8000) and a public tunnel to it, for example
   `ngrok http 8000`. Note the public `https://...` base URL.
3. Set `PUBLIC_BASE_URL` in `.env` to that base URL, no trailing slash, then restart the app.
   Twilio signs the exact URL it calls, so a mismatch makes every real request a 403.
4. In the Twilio console, on the number's Configure page, set **A call comes in** to
   **Webhook**, `POST`, URL `<PUBLIC_BASE_URL>/webhooks/missed-call`. Save.
5. Check: call the number. The app logs `missed call CA...: stored`, and the caller hears the
   fixed message. A second identical request must log `duplicate ignored`.

This replaces the TwiML Bin `forwarding-test` that [08](./08-telephony-forwarding-test.md) used
for G0b. Note which one the number points at before you run the G0b forwarding test again.

### Make the auto-SMS able to send
Blocks: the missed-call text actually reaching a phone (#20). The code is built and tested with
a fake sender, but it has never sent a real message. Until these are set the app logs
`twilio is not configured, no sms sent` and still stores the call.

1. Put these in `.env`: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`
   (an SMS-capable Twilio number, E.164 like `+447...`) and `BUSINESS_NAME` (shown in the text,
   for example `Dave's Joinery`).
2. A Twilio **trial** account can only text numbers you have verified in the console, and
   prefixes the message. Verify your own mobile for testing, or upgrade the account.
3. Check whether the number needs UK regulatory registration before it can send SMS to UK
   phones. This has not been checked.
4. Check: call the Twilio number from a verified phone. Within a few seconds a text arrives
   that names the business and asks for a reply. A Twilio retry of the same call must not send
   a second text.
5. Decide whether a caller ringing the Twilio number back should hear more than the fixed
   message (see D-011).

### Repository setting: delete merged branches
Settings -> General -> "Automatically delete head branches". Merged PR branches currently
stay on GitHub.

## Done

Nothing yet.

## Change history

- **0.2 (2026-11-07)** — added the auto-SMS configuration step from #20.
- **0.1 (2026-11-07)** — created with the webhook step from #18 and the branch-cleanup setting.
