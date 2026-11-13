# agent-ant ops scheduler (CDK)

EventBridge Scheduler -> ECS Fargate one-off tasks that run the retry/purge scripts on the same
image as the API, because App Runner has no native cron (#96, D-028).

- `retry-sms` — every ~5 minutes
- `retry-extractions` — every ~5 minutes
- `purge` — daily at 03:00 UTC

This app is a **standalone uv project** (not a workspace member), so `aws-cdk-lib` stays out of
the main dev environment. Deploy with the AWS CDK CLI (Node), which runs `python app.py` through
`uv run`:

```bash
# one-off: npx downloads the cdk CLI, uv installs aws-cdk-lib into .venv
cd infra/cdk
npx --yes aws-cdk@latest synth \
  -c accountId=<account> \
  -c awsRegion=eu-west-2 \
  -c imageUri=<account>.dkr.ecr.eu-west-2.amazonaws.com/agent-ant-api:latest \
  -c databaseUrlSecretArn=arn:aws:secretsmanager:eu-west-2:<account>:secret:... \
  -c twilioAuthTokenSecretArn=arn:aws:secretsmanager:eu-west-2:<account>:secret:... \
  -c twilioAccountSid=AC... \
  -c twilioFromNumber=+447... \
  -c vpcId=vpc-...
npx --yes aws-cdk@latest diff   # same -c flags
npx --yes aws-cdk@latest deploy # same -c flags
```

or, from the repo root, `just cdk-synth` / `cdk-diff` / `cdk-deploy` (pass the `-c` flags through).

## Context keys

| Key | Required | Meaning |
|---|---|---|
| `accountId` | yes | AWS account id; sets the stack's `env` so `Vpc.from_lookup` can resolve. |
| `awsRegion` | no | Default `eu-west-2`. |
| `imageUri` | yes | ECR image (the same one App Runner serves). |
| `databaseUrlSecretArn` | yes | Secrets Manager ARN holding the Supabase `DATABASE_URL`. |
| `twilioAuthTokenSecretArn` | yes | Secrets Manager ARN holding `TWILIO_AUTH_TOKEN`. |
| `twilioAccountSid` | yes | Twilio account SID (non-secret). |
| `twilioFromNumber` | yes | The Twilio number, E.164. |
| `vpcId` | yes | VPC id; the task runs in its **public** subnets (selected by type). |
| `businessName` | no | Shown in the auto-SMS template. |
| `publicBaseUrl` | no | Base URL Twilio calls; enables the SMS status callback. |
| `llmProvider` | no | Default `bedrock`. |
| `llmModel` | no | Default `eu.anthropic.claude-sonnet-4-6`. |
| `retryRateMinutes` | no | Default `5`. |

The two secrets are the ones `docs/10-manual-steps.md` already has App Runner read, so this stack
reuses them rather than duplicating them. Nothing secret belongs in this file or in `cdk.json`.