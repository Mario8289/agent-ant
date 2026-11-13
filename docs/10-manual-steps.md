---
title: Manual Steps — things only you can do
status: draft
version: 0.20
last_updated: 2026-11-13
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

`HELP`/`STOP` handling is implemented (#72, D-019): STOP opts the caller out and is confirmed
with a fixed text, HELP answers with the reply-to-here instructions. Both are fixed templates
(D-004).

### LLM credentials for Week 2 — Bedrock
Blocks: the extraction agent (#22, #23). Nothing runs without a provider. Bedrock is the Week 2
provider (D-009, D-015): `eu-west-2` (London), EU-geography inference (`eu.*` profiles accepted).

- [x] AWS account with billing enabled (2026-11-10). The account holder is who the DPA attaches
  to. A spend guard (budget + SCP action) is set up — see **Reference -> Bedrock spend guard**.
- [x] Create an IAM user for local development rather than using root: `agent-ant-user`, in the
  member account `817210752440` (verified 2026-11-10), so the SCP spend guard covers it. Its
  inline policy `BedrockInvokeEuSonnet55` allows `InvokeModel`/`InvokeModelWithResponseStream`
  on the `eu.anthropic.claude-sonnet-4-6` inference profile and foundation model (`InvokeModel`
  also covers the `Converse` API the code uses; the policy name is now stale — it points at 4.6,
  see D-016). Put the access key in `~/.aws/credentials` via
  `aws configure --profile agent-ant` (region `eu-west-2`) — the app reads `AWS_PROFILE` and does
  **not** read access keys from `.env`.
- [x] Enable London (`eu-west-2`) for the member account (2026-11-10). Both the region SCP and
  the console's Visible Regions had to change — see **Reference -> Bedrock region**.
- [ ] In the console, region **eu-west-2**, open Bedrock -> **Model access** and request the
  model chosen for #22. Anthropic models ask for a use case (the catalog shows a banner for
  first-time users to submit details) and can take days; Amazon's models are usually instant. A
  model listed in `us-east-1` is not necessarily offered in London. An `eu.*` cross-region
  profile is accepted (D-015) and stays in EU geography; avoid `global.*`, which can route
  outside the EU. **Account gating:** Sonnet 5/5.5 and Opus 5.5 return "not available for this
  account" for `817210752440` even via `global.*` (it is an entitlement check, not routing);
  Sonnet 4.6 and Haiku 4.5 work (D-016). Request newer models from AWS Sales/Support, then swap
  the `.env` id and IAM ARNs back.
- [ ] Set `LLM_PROVIDER=bedrock`, `LLM_MODEL=eu.anthropic.claude-sonnet-4-6` and
  `AWS_PROFILE=agent-ant` in `.env` (D-016). `LLM_API_KEY` stays empty, and do **not** set
  `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` in `.env` — the app reads `AWS_PROFILE` →
  `~/.aws/credentials`, not keys from `.env`. `LLM_MODEL` is a foundation-model id or an `eu.*`
  inference profile (D-015); never `global.*`.
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

### Deploy the API to AWS App Runner + Supabase (Week 4, #29)
Blocks: a real customer's call reaching the service (#31). Hosting choice is AWS App Runner
(D-020); the database is Supabase (docs/05) and the LLM is Bedrock (D-018). The app is
stateless, so only the database holds customer data — Supabase's region is the residency
surface, not the app host.

**Supabase (Postgres)**

- [ ] Create a Supabase project. Choose a region inside the EU/UK (e.g. London or a `eu-*`
  region); the database holds caller numbers and message bodies, so keep it in EEA/adequate
  geography. The free tier pauses after 7 days of inactivity and is 500 MB; for anything
  beyond the Week 4 live test, move to a paid tier with a DPA (same reasoning as R4).
- [ ] Copy the **direct connection** (or **session pooler**, port 5432) string from
  Settings -> Database -> Connection string. Change the scheme to the psycopg driver the app
  uses: `postgresql://…` becomes `postgresql+psycopg://…`. Keep `?sslmode=require` (Supabase
  requires TLS). This becomes `DATABASE_URL`.
- [ ] Run the migrations against it once, from the repo:
  `DATABASE_URL="<the string>" uv run alembic upgrade head`. The app creates no schema itself;
  a deploy without this step starts but every request 500s.

**Image (ECR)**

- [ ] Create a repository: `aws ecr create-repository --repository-name agent-ant-api --region eu-west-2`.
- [ ] Log Docker in: `aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.eu-west-2.amazonaws.com`.
- [ ] Build and push (the `Dockerfile` is at the repo root):
  `docker build -t agent-ant-api .` then
  `docker tag agent-ant-api:latest <account>.dkr.ecr.eu-west-2.amazonaws.com/agent-ant-api:latest`
  and `docker push <account>.dkr.ecr.eu-west-2.amazonaws.com/agent-ant-api:latest`.

**App Runner service**

- [ ] Create a service from **Container registry** pointing at the ECR image. Port **8000**.
  Let App Runner create the *service role* (ECR pull) automatically.
- [ ] Create an **instance role** for Bedrock and attach it to the service. It needs the invoke
  policy under **Reference -> Bedrock IAM policy**, narrowed to the model's ARN at lock-in (the
  existing note). No `AWS_PROFILE` and no keys: boto3 in the container picks up the instance
  role through the metadata service.
- [ ] Set the health check path to `/health` (liveness — process is up). `/ready` also exists
  and checks the database; keep it for external monitoring rather than App Runner's own check,
  so a transient Supabase blip does not restart the instance.
- [ ] Add environment variables:
  - `ENVIRONMENT=production`, `LOG_LEVEL=INFO`
  - `DATABASE_URL` (Supabase string from above)
  - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, `BUSINESS_NAME`
  - `PUBLIC_BASE_URL=https://<the App Runner service URL>` (no trailing slash — Twilio signs
    the exact URL, so a mismatch 403s every real request)
  - `LLM_PROVIDER=bedrock`, `LLM_MODEL=eu.anthropic.claude-sonnet-4-6`, `AWS_REGION=eu-west-2`
  - Put `TWILIO_AUTH_TOKEN` and `DATABASE_URL` in AWS Secrets Manager and reference them as
    `secretsmanager:` ARNs; the rest are safe as plain variables. Do **not** set `AWS_PROFILE`
    or `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`.

**Point Twilio at the deployed service**

- [ ] With the service live, `curl https://<service-url>/health` returns `{"status":"ok",
  "environment":"production"}` and `/ready` returns 200 (database reachable).
- [ ] Repoint the Twilio webhooks to `https://<service-url>/webhooks/missed-call` and
  `/webhooks/sms-reply` (`just repoint`, or by hand — see **Reference -> Setting both webhooks
  through the API**), and set `PUBLIC_BASE_URL` to the same base.
- [ ] Check end-to-end with a real phone: a missed call logs `stored` and sends the text; a
  reply logs `stored` and produces a captured job on the dashboard.

### Schedule the retry and purge commands (Week 5, #34)

Blocks: nothing silently lost, and personal fields not kept past their line. The recovery and
retention commands are scripts, not self-scheduling (D-023, D-024, D-025), so until they run on a
schedule a failed send or extraction sits `failed` forever and outbound `to`/`body` age past 30
days.

- [ ] Schedule `just retry-sms` (re-attempt failed sends) and `just retry-extractions` (re-run
  failed extractions) to run every few minutes against the deployed database — an App Runner
  scheduled job, an EventBridge rule, or a cron on the same image. Both scripts live in
  `scripts/` and need the same env as the service (`DATABASE_URL`, Twilio, Bedrock).
- [ ] Schedule `just purge` (redact outbound `to`/`body` older than 30 days) daily.

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

### Bedrock region — London (eu-west-2)

In-region (on-demand) inference stays in one region; `eu.*` cross-region stays in EU geography
(D-015). Two separate settings had to change before London was available to the member account
(2026-11-10):

- **Region SCP.** In the management account, Organizations → Policies → Service control policies →
  `AdvancedModeRegionRestrictionSecurityControlPolicy` (p-6mega3lz). Added `eu-west-2` to the
  `RegionFloor` statement's allowed `aws:RequestedRegion` list. The policy is attached at Root,
  so every member account can now use London (Stockholm stays allowed).
- **Visible Regions.** In `agent-ant` (817210752440), Settings → Unified settings → Account
  settings → Visible Regions → tick London. The SCP alone is not enough: the console still showed
  "Region Europe (London) restricted" until this was ticked.

After both, Bedrock → Model catalog under `agent-ant` opens in eu-west-2 (82 serverless models).
The SCP is organisation-wide, but Visible Regions is per-account, so any other member account
still needs its own toggle to see London in its console.

Choosing a model: many catalog entries are labelled **Cross-region inference**. An `eu.*` profile
stays in EU geography and is accepted (D-015); a `global.*` profile can route outside the EU and
is rejected. An in-region (on-demand) model stays in one region and is also fine.

### Bedrock spend guard (SCP + budget action)

Hard-stops Bedrock spend rather than only emailing. A budget action attaches a deny SCP to an OU
at a threshold. SCPs cannot be overridden by the member account — but they do **not** apply to
the management account, so the guard only covers accounts inside the target OU.

Created 2026-11-10, all in the management account `716189571196` (ant-team):

- **SCP** `BudgetsSpendLimitDenyBedrockUsage` — a deny that blocks Bedrock model calls.
- **OU** `Workloads` (`ou-09c8-0wtd89zw`), containing the member account `agent-ant`
  (`817210752440`).
- **Role** `BudgetsDenyBedrockActionRole` — trusted by `budgets.amazonaws.com`; inline policy
  `BudgetsDenyBedrockActionRolePolicy` allows `organizations:AttachPolicy`/`DetachPolicy` on the
  SCP ARN and the Workloads OU.
- **Budget** `Monthly-20USD-Bedrock-Guard` — monthly, $20, unblended, excluding Credit and
  Refund. Email alerts at 50/75/90/95% to the account email; at 95% an SCP action attaches the
  deny policy to Workloads, run automatically.

Still to verify before the first call:

- [ ] **Which account `agent-ant-user` is in.** The guard only works if the app calls Bedrock
  from `817210752440` (in Workloads). If the user is in the management account, the SCP never
  fires.
- [ ] **SCP content.** Must deny `bedrock:Converse` and `bedrock:ConverseStream` too (the code
  uses Converse, not just `InvokeModel`). A `bedrock:*` deny is the safe choice.
- [ ] **Reverse action.** The SCP stays attached once applied; add a reverse action at a lower
  threshold, or note that a human must detach it after the spend is resolved.
- [ ] **Alert emails arrive.** Confirm the 50% email reaches the account-holder inbox.

## Change history

- **0.20 (2026-11-13)** — added the Week 5 step to schedule the retry and purge commands (#34,
  D-023/D-024/D-025).
- **0.19 (2026-11-13)** — added the Week 4 deployment entry: Supabase, ECR, App Runner
  (D-020), secrets and the Twilio repoint.
- **0.18 (2026-11-13)** — HELP/STOP opt-out implemented (#72, D-019); removed the deferral note.
- **0.17 (2026-11-10)** — D-016: extraction model is `eu.anthropic.claude-sonnet-4-6` (newer
  Claude models account-gated for `817210752440`); noted the IAM policy name is stale.
- **0.16 (2026-11-10)** — D-015: `eu.*` cross-region inference is now the accepted route; updated
  the single-region guidance and the `.env` auth note (keys in `~/.aws/credentials`, not `.env`).
- **0.15 (2026-11-10)** — confirmed `agent-ant-user` is in the member account `817210752440`
  (covered by the SCP guard); noted its scoped inline policy and that the access key goes in
  `~/.aws/credentials`, not `.env`.
- **0.14 (2026-11-10)** — documented the Bedrock region enablement (region SCP + Visible Regions)
  and the cross-region-inference caveat for D-009.
- **0.13 (2026-11-10)** — recorded the Bedrock spend guard (SCP + budget action) and its
  verification checklist; ticked the AWS account and IAM-user steps.
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
