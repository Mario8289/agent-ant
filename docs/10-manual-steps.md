---
title: Manual Steps — things only you can do
status: draft
version: 0.12
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

### LLM credentials for Week 2 — Bedrock
Blocks: the extraction agent (#22, #23). Nothing runs without a provider. Bedrock is the Week 2
provider (D-009): `eu-west-2` (London), single-region inference.

- [ ] AWS account with billing enabled. Bedrock is not covered by the free tier, and the account
  holder is who the DPA attaches to. Set a budget alarm before the first call (a few pounds a
  month is enough at this volume).
- [ ] Create an IAM user for local development rather than using root, attach the policy in
  **Reference -> Bedrock IAM policy**, then:
  `aws configure --profile agent-ant` (region `eu-west-2`). Credentials stay in
  `~/.aws/credentials`, never in the repo or `.env`.
- [ ] In the console, region **eu-west-2**, open Bedrock -> **Model access** and request the
  model chosen for #22. Anthropic models ask for a use case and can take days; Amazon's models
  are usually instant. A model listed in `us-east-1` is not necessarily offered in London.
- [ ] Set `LLM_PROVIDER=bedrock`, `LLM_MODEL=<id>` and `AWS_PROFILE=agent-ant` in `.env`;
  `LLM_API_KEY` stays empty. Use the plain model id, not an `eu.` inference profile, unless the
  model is only offered that way — a cross-region profile can route outside the UK.
- [ ] Run `just check-llm`. It prints the models the region actually offers, then sends one
  prompt to `LLM_MODEL` and prints the reply, tokens and latency. It stops before the call with
  a specific message if credentials, region or model access are wrong.
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

### Setting both webhooks through the API

`just repoint` runs `scripts/set_twilio_webhooks.py`, which writes both endpoints from
`PUBLIC_BASE_URL` and prints the before/after values. It exists because a quick tunnel rotates
its hostname and because the two webhooks are separate fields that are easy to half-update.

They are properties of the phone number resource, not separate objects:

- `voice_url` + `voice_method` (`POST`) for `<PUBLIC_BASE_URL>/webhooks/missed-call`
- `sms_url` + `sms_method` (`POST`) for `<PUBLIC_BASE_URL>/webhooks/sms-reply`

The same two fields the console form edits, so the API and the UI can be used interchangeably.
Equivalent request for one of them:

```bash
curl -X POST \
  "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/IncomingPhoneNumbers/$NUMBER_SID.json" \
  --data-urlencode "VoiceUrl=$PUBLIC_BASE_URL/webhooks/missed-call" \
  --data-urlencode "VoiceMethod=POST" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"
```

Two gotchas: `TWILIO_FROM_NUMBER` must be E.164 with the leading `+`, or the number lookup
returns nothing and the update silently does nothing; and the URL written here must match the
app's `PUBLIC_BASE_URL` exactly, because Twilio signs the URL it called.

### When the tunnel URL changes

A quick tunnel (`cloudflared` with no account, or free ngrok) gets a new hostname on every
restart, and the webhook breaks silently: Twilio keeps calling the dead URL. All three places
must change together, or the app answers 403 because the signature no longer matches.

1. Start the tunnel again and copy the new `https://...` base URL.
2. Update `PUBLIC_BASE_URL` in `.env` (no trailing slash), then run `just repoint` and restart
   `just dev`.
3. `just repoint` sets **A call comes in** and **A message comes in** from that one value, and
   prints before/after so you can see it worked. Doing it by hand instead is two fields on the
   same console page (see above); missing one leaves a working call path with a dead reply path.
   Use **Monitor -> Logs -> Errors** in the console to confirm Twilio is reaching the app, not a
   stale hostname.

Symptoms of forgetting step 2 or 3: Twilio errors in the console with no request in the app
log (dead URL), or a `403 Invalid Twilio signature` in the app log (stale
`PUBLIC_BASE_URL`). Forgetting both looks identical to Twilio, so check the two values match
before debugging anything else.

The permanent fix is a named Cloudflare tunnel on a domain, which keeps one hostname across
restarts, or deploying the API. Neither is needed while the data is synthetic; both are needed
before a real customer's call reaches this service.

### Bedrock IAM policy

Minimum policy for local development. `Resource: "*"` is acceptable for synthetic data; at the
Week 4 lock-in (#29) narrow the invoke statements to the chosen model's ARN.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListModels",
      "Effect": "Allow",
      "Action": [
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel",
        "bedrock:ListInferenceProfiles",
        "bedrock:GetInferenceProfile"
      ],
      "Resource": "*"
    },
    {
      "Sid": "InvokeModels",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

`InvokeModel` also covers the `Converse` API that `just check-llm` and the Week 2 adapter use.
Model access is a separate grant from IAM: the policy lets the user call Bedrock, but each
model still has to be enabled in **Model access** for that region.

## Change history

- **0.12 (2026-11-09)** — restored `just repoint` (the recipe, script and API documentation
  were dropped from the #75 squash merge); `just check-llm` documented alongside it.
- **0.11 (2026-11-08)** — LLM entry rewritten as executable Bedrock steps (IAM user, model
  access, region, `just check-llm`); the IAM policy is under **Reference**.
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
