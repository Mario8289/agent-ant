# 0002 — LLM provider: keep it swappable for the MVP, lock a DPA-backed provider before live traffic

- **Status:** accepted
- **Date:** 2026-11-05
- **Decision log entry:** D-009
- **Superseded in part by:** D-015 (2026-11-10) — the single-region `eu-west-2` constraint is
  relaxed to EU cross-region (`eu.*` profiles). See spikes/06-uk-eea-data-residency.md.

## Context

The product sends a customer's message — name, phone number, address, job description — to an
LLM for extraction. That is personal data under UK GDPR, so whichever provider processes it is
a **processor**, and we need an Article 28 data-processing agreement, a lawful transfer
mechanism, and a no-training commitment. This is risk **R4** in
[05-architecture-and-schema.md](../05-architecture-and-schema.md).

Two facts shape the decision:

1. **Nothing real is being sent yet.** G0a (interviews) and G0b (carrier forwarding) are not
   passed, so there is no live traffic. Development and evals use synthetic messages only.
2. **The founder does not want to be locked in before the MVP is proven.** Picking a model now
   and tuning prompts and evals to it makes a later switch expensive for no present benefit.

The first draft of this ADR recommended the paid Anthropic API immediately. The founder chose
instead to stay provider-agnostic during the MVP and tighten up afterwards. That is compatible
with the repo rule in `AGENTS.md`, which requires a DPA **before live traffic**, not before the
first line of code.

## Decision

**During the MVP, the LLM provider is not fixed. Use whatever is available and cheapest for
synthetic-data development. Lock one DPA-backed provider before Dad goes live in Week 4.**

Two rules do not move:

1. **Synthetic data only** until a paid, DPA-backed account is in place. No real customer names,
   phone numbers, addresses or job details — not in prompts, not in logs, not in eval fixtures.
2. **Before live traffic** (Week 4, [#29](https://github.com/Mario8289/agent-ant/issues/29)),
   one provider is locked with an executed DPA, a confirmed no-training commitment, and a
   re-run of the golden set against that model. Until then R4 stays open.

**Bedrock is the default choice when credentials allow it.** It is the cheapest route to a
compliant setup because it comes with an AWS DPA, a contractual no-training commitment, and the
London region:

- AWS states that "AWS and the third-party model providers will not use any inputs to or outputs
  from Amazon Bedrock to train" the models.
- Bedrock has a London endpoint (`eu-west-2`). Use **single-region inference**, not a
  cross-region inference profile, if the requirement is UK-only processing. Confirm the chosen
  model's availability in London when Week 2 starts — regional catalogues lag `us-east-1`.
- The AWS GDPR DPA covers the processing; confirm the UK transfer addendum at lock-in.
- AWS Activate credits apply, and [04-grants-timeline.md](../04-grants-timeline.md) already lists
  them.

If the existing developer credentials do not have Bedrock model access, use any other paid API
for now. Do not spend MVP time on provider procurement.

**Engineering consequence — keep the seam:**

- One small adapter module (`agents/missed_call/llm/`) exposing a single `extract()` call that
  takes text and returns the validated Pydantic object. Provider SDKs are imported only there.
- `llm_provider` and `llm_model` in `Settings` select the adapter; adding a provider is a new
  module plus config, not a change to the graph or the schema.
- The audit row already records `model` and `prompt_version`, so switching is measurable.
- Prompts stay versioned files and provider-neutral; no provider-specific prompt forks.

## Options for the Week 4 lock-in

| | AWS Bedrock | Anthropic API | OpenAI API | Google Vertex AI |
|---|---|---|---|---|
| **UK contracting entity** | Per the AWS service terms (EMEA entity) | Anthropic Ireland Ltd | OpenAI OpCo LLC (US) | Google Cloud EMEA Ltd |
| **UK in-region inference** | Yes, `eu-west-2` (single-region) | No | No | Yes, `europe-west2` (model-dependent) |
| **Training on customer data** | Not used for training | Contractually prohibited | Not by default | Not used on the paid tier |
| **Setup cost** | AWS account + model access | API key | API key + DPA form | GCP project + Vertex setup |
| **Why it might win** | UK region + AWS credits + existing credentials | Simplest contract, strongest wording | Model choice and price | UK region, strong structured output |

The choice is deliberately left open until there is an eval to compare against. Cost at this
volume is pennies per month for all four, so the deciding factors will be UK residency,
contract terms and extraction accuracy — not price.

## Consequences

**Easier:** no procurement blocking the build; prompts and evals can be developed against
whichever model is at hand; switching is a config change.

**Harder / accepted:**

- **R4 remains open until Week 4.** This is the main risk being carried. The mitigation is the
  synthetic-data rule and the explicit Week 4 gate, not a signed contract today.
- Prompts tuned to one model may need re-tuning after the switch. The golden set is the defence:
  it measures the new model rather than assuming parity.
- Two credential paths to maintain during development (whatever is available now, and the final
  provider later).
- If a real customer message arrives before Week 4, it must not be sent to the LLM. Capture it,
  reply with the fixed template, and handle extraction manually.

**Bedrock credential note:** Bedrock authenticates with the standard AWS credential chain (IAM
access keys, a profile, SSO or an instance role), not an API key. Developer or sandbox
credentials are fine for synthetic data, but they are not a substitute for an AWS account you
control when real data arrives — the DPA and the data-processing obligations attach to the
account holder.

**Revisit:** at the Week 4 gate, or earlier if real traffic starts sooner than planned.

## Source

- Founder decision, 2026-11-05 — provider-agnostic for the MVP, Bedrock preferred
- [AGENTS.md](../../AGENTS.md) rule 5 — synthetic data only; DPA before live traffic
- [Amazon Bedrock FAQ](https://aws.amazon.com/bedrock/faqs/) — no training on inputs or outputs
- [Amazon Bedrock data protection](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)
  — model providers have no access to prompts or completions
- [05-architecture-and-schema.md](../05-architecture-and-schema.md) — risk R4
- [04-grants-timeline.md](../04-grants-timeline.md) — AWS Activate credits

> This ADR records a technical and commercial choice, not legal advice. The DPA must be executed
> against the correct legal entity before live data, and a copy kept.
