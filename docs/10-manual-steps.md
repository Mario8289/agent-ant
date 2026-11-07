---
title: Manual Steps — things only you can do
status: draft
version: 0.4
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

### Confirm the Twilio number can send and receive SMS, and point replies at the app
Blocks: the caller's reply reaching the app (#21). The number bought for the G0b forwarding
test was chosen for voice; a voice-only number cannot send the auto-text or receive replies.

1. In the console, on the number's Configure page, check the **Capabilities** show SMS as well
   as Voice. If not, buy an SMS-capable number and use that for `TWILIO_FROM_NUMBER`.
2. Set **A message comes in** to **Webhook**, `POST`, URL
   `<PUBLIC_BASE_URL>/webhooks/sms-reply`. Save. Do this after #21 is merged; until then the
   path does not exist and Twilio's request will 404.
3. Check: reply to the auto-text from a verified phone. The app logs the reply as stored, and
   a repeat of the same `MessageSid` logs a duplicate.

### LLM credentials for Week 2
Blocks: the extraction agent (#22, #23). Nothing runs without a provider.

1. Bedrock (the default, D-009): in the AWS console, region **eu-west-2 (London)**, open
   Bedrock -> Model access and request access to the model chosen for #22. Access is not
   instant on some models, so do this early.
2. Set `LLM_PROVIDER=bedrock` and `LLM_MODEL` in `.env`. Bedrock uses the AWS credential chain
   (an AWS profile or access keys in the environment), so `LLM_API_KEY` stays empty. Check the
   chosen model is offered in `eu-west-2`; use single-region inference, not a cross-region
   profile.
3. Synthetic data only until the Week 4 DPA gate (#16, R4). Do not send Dad's real customers'
   messages to any provider before then.

### Check the Twilio account region
Blocks: the Week 4 DPA gate (#16). The region decides where Twilio stores call and message
data, and it is set per account, so it is awkward to change later.

1. Find whether the account is US1 or IE1 (console footer or account settings).
2. If it is US1 and a UK/EU data location is wanted, check what moving involves before Week 4.

### Repository setting: delete merged branches
Settings -> General -> "Automatically delete head branches". Merged PR branches currently
stay on GitHub.

## Done

Nothing yet.

## Change history

- **0.4 (2026-11-07)** — LLM step now Bedrock-specific: model access request in eu-west-2.
- **0.3 (2026-11-07)** — added the SMS capability and reply-webhook step (#21), LLM credentials
  for Week 2, and the Twilio account region check.
- **0.2 (2026-11-07)** — added the auto-SMS configuration step from #20.
- **0.1 (2026-11-07)** — created with the webhook step from #18 and the branch-cleanup setting.
