# Spike 06: UK data residency when Bedrock routes outside London

## Question

Is there a regulatory problem if the extraction agent sends caller message text to a Bedrock
model through the EU cross-region inference profile (`eu.` prefix), which can route the request
to EU regions outside the UK (Ireland, Frankfurt, Paris, Milan, Spain, Stockholm)?

## Why it matters

D-009 chose `eu-west-2` (London) single-region inference to keep data in the UK. London offers
only a couple of Claude models in-region, so the proposal is to widen to the EU cross-region
profile to unlock more models and burst capacity. That is a change to D-009, so it needs
evidence before it is accepted.

R4 (#16) — a DPA-backed provider that does not train on data — is a separate question from
*where* the data is processed. This spike is only about residency, not training.

## Method

Desk research: UK GDPR transfer rules (post-Brexit adequacy), AWS Bedrock cross-region inference
semantics, and Anthropic-on-Bedrock data handling.

## Findings

1. **UK ↔ EEA transfers are lawful without extra safeguards.** The EU renewed its UK adequacy
   decisions on 19 December 2025 (valid until 27 December 2031), and the UK's own regulations
   recognise the EEA as adequate. Data leaving the UK for an EEA region is not a "restricted
   transfer", so no Standard Contractual Clauses or transfer impact assessment is required.
2. **The `eu.` inference profile stays inside Europe.** AWS documents geographic cross-region
   inference as "within geographic boundaries (e.g. all EU Regions); prompts and outputs may move
   within the geography but not outside it". The `eu.` profile routes across EEA regions (plus
   Zurich in some listings — Switzerland also has adequacy). It does not use US regions.
3. **The `global.` profile is the one to avoid.** It has no geographic restriction and can route
   to any commercial region, including the US. This is the actual residency risk, not the `eu.`
   profile.
4. **No training either way.** Bedrock does not train on customer inputs, and Anthropic-on-Bedrock
   runs on AWS-managed infrastructure with zero operator access. R4's "no training" is satisfied
   regardless of region; this spike covers only the residency half.

## Conclusion

No regulatory blocker to using the EU cross-region profile, provided the profile is the `eu.`
(geographic) one — never `global.` — and the chosen model's region list is EEA/adequate-only.

## Done when

- [ ] The chosen model's `eu.` inference profile is confirmed EEA/adequate-only:
      `aws bedrock get-inference-profile --inference-profile-identifier eu.<model-id> --region eu-west-2`
      prints a `models` list with no US region.
- [ ] The region SCP (`AdvancedModeRegionRestrictionSecurityControlPolicy`) is tightened for the
      residency goal: it currently allows `us-east-1` and `us-west-2` in the `RegionFloor` list,
      and it does not deny the `global.*` inference profile. Both should be fixed before any real
      data flows — allow the EU regions the profile routes to, and deny `global.*`.
- [x] Decision recorded (D-015) changing D-009 from single-region London to EU geography, with
      this spike cited as the evidence.

## Sources

- EU adequacy decision renewal, 19 Dec 2025:
  https://ec.europa.eu/commission/presscorner/detail/en/ip_25_3059
- AWS cross-region inference:
  https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html
- AWS regional model availability (in-region vs geo vs global):
  https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html
- AWS blog, EU cross-region inference profiles and region lists:
  https://aws.amazon.com/blogs/alps/unlocking-ai-flexibility-in-switzerland-a-guide-to-cross-region-inference-for-eu-data-processing-and-model-access/
