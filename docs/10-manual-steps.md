---
title: Manual Steps — things only you can do
status: draft
version: 0.1
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

### Repository setting: delete merged branches
Settings -> General -> "Automatically delete head branches". Merged PR branches currently
stay on GitHub.

## Done

Nothing yet.

## Change history

- **0.1 (2026-11-07)** — created with the webhook step from #18 and the branch-cleanup setting.
