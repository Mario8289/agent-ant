---
title: Manual Steps — things only you can do
status: draft
version: 0.10
last_updated: 2026-11-08
---

# 10 — Manual Steps

Things the code cannot do for itself: console clicks, accounts, real phones. Each entry says
what blocks on it. A step is ticked only when it is actually done, with the date where it
helps. An entry moves to **Done** only when every step under it is ticked. Procedures worth
keeping after an entry closes live under **Reference**.

## Open

### Make the auto-SMS able to send
Blocks: the missed-call text actually reaching a phone (#20).

- [x] Put these in `.env`: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` (an
  SMS-capable Twilio number, E.164 like `+447...`, leading `+` included) and `BUSINESS_NAME`
  (shown in the text, for example `Dave's Joinery`).
- [x] Trial-account limits: a trial account can only text numbers you verified in the console
  and prefixes the message. This account is **Full**, not trial (checked 2026-11-08), so that
  does not apply; it would again if the account were downgraded or a new one used.
- [x] Check whether the number needs UK regulatory registration before it can send SMS to UK
  phones. **No further registration needed** (checked 2026-11-08). Twilio has required an
  approved UK regulatory bundle for long codes since 30 September 2024
  ([changelog](https://www.twilio.com/en-us/changelog/new-kyc-regulation-for-the-uk-long-codes)),
  and the API shows one already attached: bundle `BUb3f0ac7c191ef6ebe850ff539f52334e`
  (`Ant-Registration-1`, `twilio-approved`), number +447533021710 status `in-use`,
  `address_requirements: none`. Twilio's
  [GB SMS guidelines](https://www.twilio.com/en-us/guidelines/gb/sms) list domestic long codes
  as supported with sender ID preserved and provisioning time `N/A`;
  sender-ID pre-registration applies only to alphanumeric "Protected Sender IDs", not to
  numeric senders.
- [x] Check: call the Twilio number from a real phone. Done 2026-11-08: within a few seconds a
  text arrived naming the business and asking for a reply. Twilio reports it `delivered`
  (`SMef63a36ded480867a19702fc1f51a67f`). A retry of the same call sends no second text: the
  SMS is only queued when the `CallSid` is first stored. Twilio also *attempts* SMS to
  landlines, where some carriers convert it to a voice call, so a landline is not a safe test.
- [ ] Decide whether a caller ringing the Twilio number back should hear more than the fixed
  message (see D-011).

`HELP`/`STOP` handling is deferred: the guideline applies to real end users, and the
prototype only uses synthetic data and test calls. Tracked in
[#72](https://github.com/Mario8289/agent-ant/issues/72), needed before the Week 4 gates.

### LLM credentials for Week 2
Blocks: the extraction agent (#22, #23). Nothing runs without a provider.

- [ ] Bedrock (the default, D-009): in the AWS console, region **eu-west-2 (London)**, open
  Bedrock -> Model access and request access to the model chosen for #22. Access is not
  instant on some models, so do this early.
- [ ] Set `LLM_PROVIDER=bedrock` and `LLM_MODEL` in `.env`. Bedrock uses the AWS credential
  chain (an AWS profile or access keys in the environment), so `LLM_API_KEY` stays empty. Check
  the chosen model is offered in `eu-west-2`; use single-region inference, not a cross-region
  profile.
- [ ] Synthetic data only until the Week 4 DPA gate (#16, R4). Do not send Dad's real
  customers' messages to any provider before then.

### Check the Twilio account region
Blocks: the Week 4 DPA gate (#16). The region decides where Twilio stores call and message
data, and it is set per account, so it is awkward to change later.

- [x] Find whether the account is US1 or IE1. **US1.** The number's voice configuration shows
  **Active region: United States (US1)**, and the API response header reports
  `X-Home-Region: us1` (checked 2026-11-08).
- [ ] If it is US1 and a UK/EU data location is wanted, check what moving involves before
  Week 4.

### Repository setting: delete merged branches
- [ ] Settings -> General -> "Automatically delete head branches". Merged PR branches
  currently stay on GitHub.

## Done

### Point the Twilio number at the missed-call webhook — 2026-11-08
Blocks: a real forwarded call reaching the app (#18).

- [x] Put the Twilio auth token in `.env` as `TWILIO_AUTH_TOKEN`. Without it the endpoint
  refuses every request (503) by design.
- [x] Run the app (`just dev`, port 8000) and a public tunnel to it, for example
  `cloudflared tunnel --url http://localhost:8000` (no account needed) or `ngrok http 8000`.
  Note the public `https://...` base URL.
- [x] Set `PUBLIC_BASE_URL` in `.env` to that base URL, no trailing slash, then restart the app.
  Twilio signs the exact URL it calls, so a mismatch makes every real request a 403.
- [x] Set the number's voice webhook to **Webhook**, `POST`,
  `<PUBLIC_BASE_URL>/webhooks/missed-call`. Done through the API on 2026-11-08 and checked in
  the One Console afterwards; by hand it is **Edit configuration details** on the number's
  voice tab.
- [x] Check: call the number. Called from a real mobile: the app logged `missed call
  CA28eb843a90471180acc7457361ecc2ca: stored`, the caller heard the fixed message, and the
  follow-up SMS was `delivered`. Replays of the same `CallSid` log `duplicate ignored` and
  insert nothing (verified earlier with signed test requests).

This replaces the TwiML Bin `forwarding-test` that [08](./08-telephony-forwarding-test.md) used
for G0b. Note which one the number points at before you run the G0b forwarding test again.

### Confirm the Twilio number can send and receive SMS, and point replies at the app — 2026-11-08
Blocks: the caller's reply reaching the app (#21).

- [x] Check the number's **Capabilities** show SMS as well as Voice. The API reports
  `sms: true` and `voice: true` for this number (checked 2026-11-08), so no new number is needed.
- [x] Set **A message comes in** to **Webhook**, `POST`, `<PUBLIC_BASE_URL>/webhooks/sms-reply`.
  Done through the API on 2026-11-08, alongside the voice webhook; by hand it is the messaging
  tab of the same console page (see **Reference** below).
- [x] Check: reply to the auto-text. Replied from a real phone: the app logged `sms reply
  SM5f172a0f8a44cc1209d0f0c9ca604207: stored` and the row is linked to the missed call
  (`related_event_id` = 9). Idempotency on a repeated `MessageSid` is covered by the unique
  constraint and tested with signed requests.

## Reference

### Finding the setting in the Twilio console

The account lands on the **new console** (`1console.twilio.com`, "Twilio One Console");
`console.twilio.com` is the older UI. Phone numbers moved under **Numbers & senders**, and the
page is tabbed rather than one long form. Deep link for this account:

```
https://1console.twilio.com/go?to=/account/<ACCOUNT_SID>/us1/senders-hub/list/phone-numbers/inventory
```

`<ACCOUNT_SID>` is the `TWILIO_ACCOUNT_SID` value from `.env`, left as a placeholder because
the repository's push protection rejects committed Twilio account identifiers.

Select the number, open the voice configuration tab, then **Edit configuration details** in the
top right. The values are read-only until that button is pressed. The messaging tab holds
**A message comes in**.

### When the tunnel URL changes

A quick tunnel (`cloudflared` with no account, or free ngrok) gets a new hostname on every
restart, and the webhook breaks silently: Twilio keeps calling the dead URL. All three places
must change together, or the app answers 403 because the signature no longer matches.

1. Start the tunnel again and copy the new `https://...` base URL.
2. Update `PUBLIC_BASE_URL` in `.env` (no trailing slash) and restart `just dev`.
3. Re-point the number's webhooks at the new base: **A call comes in** and **A message comes
   in**, as described above. Use **Monitor -> Logs -> Errors** in the console to confirm Twilio
   is reaching the app, not a stale hostname.

Symptoms of forgetting step 2 or 3: Twilio errors in the console with no request in the app
log (dead URL), or a `403 Invalid Twilio signature` in the app log (stale
`PUBLIC_BASE_URL`). Forgetting both looks identical to Twilio, so check the two values match
before debugging anything else.

The permanent fix is a named Cloudflare tunnel on a domain, which keeps one hostname across
restarts, or deploying the API. Neither is needed while the data is synthetic; both are needed
before a real customer's call reaches this service.

## Change history

- **0.10 (2026-11-08)** — reply webhook verified with a real reply; that entry is done,
  closing the Week 1 loop.
- **0.9 (2026-11-08)** — real call and real SMS verified; the voice-webhook entry is done, and
  the console and tunnel procedures moved to **Reference**.
- **0.8 (2026-11-08)** — HELP/STOP deferred to #72; the prototype has no real end users to opt
  out.
- **0.7 (2026-11-08)** — UK SMS registration resolved: no action needed beyond the approved
  regulatory bundle already attached; added HELP/STOP and landline caveats.
- **0.6 (2026-11-08)** — steps are now checkboxes and ticked only where done; recorded the
  completed webhook, SMS configuration, capabilities and region checks with dates.
- **0.5 (2026-11-08)** — added the tunnel URL recovery procedure and where the settings live in
  the new Twilio console (One Console); recorded the account region as US1.
- **0.4 (2026-11-07)** — LLM step now Bedrock-specific: model access request in eu-west-2.
- **0.3 (2026-11-07)** — added the SMS capability and reply-webhook step (#21), LLM credentials
  for Week 2, and the Twilio account region check.
- **0.2 (2026-11-07)** — added the auto-SMS configuration step from #20.
- **0.1 (2026-11-07)** — created with the webhook step from #18 and the branch-cleanup setting.
