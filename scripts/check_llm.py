"""Check Bedrock credentials and that the configured model actually runs.

Week 2 (#22) cannot start on a guess. A Bedrock failure looks the same from the app whether
the cause is a missing AWS credential, a model that is not offered in the region, an access
grant that was never requested, or a typo in ``LLM_MODEL``. This script separates those cases
and finishes with one real call, so the agent's first invocation is not also the first time
anyone finds out the setup is wrong.

It reads ``LLM_MODEL``, ``AWS_REGION`` and ``AWS_PROFILE`` from settings, so values in ``.env``
work: pydantic-settings loads them for the app but does not export them to ``os.environ``, and
boto3 reads only the environment. ``LLM_API_KEY`` is not used — Bedrock has no API key.

Usage: ``just check-llm``.
"""

import sys
import time
from typing import Any

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    NoRegionError,
)

from agent_ant_core.config import get_settings

# London is the region chosen in D-009. Kept here as the fallback so the script works before
# ``.env`` has any AWS settings at all.
DEFAULT_REGION = "eu-west-2"
PROMPT = "Reply with the single word: ready"


def _fail(code: int, message: str) -> int:
    sys.stdout.flush()
    print(f"\n{message}", file=sys.stderr)
    return code


def _is_text_model(summary: dict[str, Any]) -> bool:
    return "TEXT" in summary.get("outputModalities", [])


def _print_models(models: list[dict[str, Any]]) -> None:
    """Print what the region offers, split by whether on-demand invocation is possible."""
    on_demand = sorted(
        m["modelId"] for m in models if "ON_DEMAND" in m.get("inferenceTypesSupported", [])
    )
    profile_only = sorted(
        m["modelId"] for m in models if "ON_DEMAND" not in m.get("inferenceTypesSupported", [])
    )
    print(f"\non-demand models in {len(on_demand)} ids:")
    for model_id in on_demand:
        print(f"  {model_id}")
    if profile_only:
        print("\nonly through an inference profile (may leave the UK):")
        for model_id in profile_only:
            print(f"  {model_id}")


def _find_profile(bedrock: Any, model_id: str) -> str | None:
    """Return an inference profile id carrying this model, if the region has one."""
    profiles = bedrock.list_inference_profiles(typeEquals="SYSTEM_DEFINED")[
        "inferenceProfileSummaries"
    ]
    for profile in profiles:
        for model in profile.get("models", []):
            if model.get("modelArn", "").endswith(model_id):
                return str(profile["inferenceProfileId"])
    return None


def main() -> int:
    settings = get_settings()
    region = settings.aws_region or DEFAULT_REGION
    profile = settings.aws_profile or None

    if settings.llm_provider and settings.llm_provider != "bedrock":
        print(
            f"warning: LLM_PROVIDER is {settings.llm_provider!r}, checking Bedrock anyway",
            file=sys.stderr,
        )

    print(f"region : {region} (D-009 target is eu-west-2 / London)")
    print(f"profile: {profile or '<default credential chain>'}")

    try:
        session = boto3.Session(profile_name=profile, region_name=region)
        identity = session.client("sts").get_caller_identity()
    except NoCredentialsError:
        return _fail(
            2,
            "no AWS credentials found. Run `aws configure --profile agent-ant`, put "
            "AWS_PROFILE=agent-ant in .env, and re-run `just check-llm`.",
        )
    except NoRegionError:
        return _fail(2, f"no AWS region resolved; set AWS_REGION={DEFAULT_REGION} in .env.")
    except (BotoCoreError, ClientError) as exc:
        return _fail(2, f"could not authenticate: {exc}")

    arn = identity["Arn"]
    print(f"identity: {arn}")
    if arn.endswith(":root"):
        print("warning: this is the root user; use a scoped IAM user for development")

    bedrock = session.client("bedrock")
    try:
        models = [
            m for m in bedrock.list_foundation_models()["modelSummaries"] if _is_text_model(m)
        ]
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code in {"AccessDeniedException", "UnrecognizedClientException"}:
            return _fail(2, "credentials cannot list models. Check the IAM policy in docs/10.")
        return _fail(2, f"listing models failed: {exc}")

    _print_models(models)

    model_id = (settings.llm_model or "").strip() or None
    if not model_id:
        return _fail(
            1,
            "LLM_MODEL is not set. Pick one of the ids above, set LLM_MODEL in .env, "
            "and re-run `just check-llm`.",
        )

    known = {m["modelId"] for m in models}
    if model_id not in known:
        profile_id = _find_profile(bedrock, model_id)
        if profile_id:
            return _fail(
                1,
                f"{model_id} is not offered as a single-region model in {region}. "
                f"It is available through inference profile {profile_id}, which can route "
                "outside the UK. D-009 asks for single-region, so prefer a model above.",
            )
        return _fail(
            1,
            f"{model_id} is not offered in {region}. It may be listed in another region, "
            "or model access was not granted. Check Bedrock -> Model access, then pick an id "
            "printed above.",
        )

    if "ON_DEMAND" not in next(m for m in models if m["modelId"] == model_id).get(
        "inferenceTypesSupported", []
    ):
        return _fail(1, f"{model_id} cannot be invoked on-demand in {region}.")

    print(f"\ninvoking {model_id} ...")
    runtime = session.client("bedrock-runtime")
    started = time.perf_counter()
    try:
        response = runtime.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": PROMPT}]}],
            inferenceConfig={"maxTokens": 32, "temperature": 0},
        )
    except ClientError as exc:
        error = exc.response.get("Error", {})
        code = error.get("Code", "Unknown")
        message = error.get("Message", "")
        if code == "AccessDeniedException":
            return _fail(
                3,
                f"access denied to {model_id}. The IAM policy allows InvokeModel, but model "
                "access for this model may not be granted. Open Bedrock -> Model access in "
                f"{region}, request the model, then retry. ({message})",
            )
        if code == "ValidationException":
            return _fail(3, f"Bedrock rejected the request: {message}")
        if code in {"ThrottlingException", "ModelNotReadyException"}:
            return _fail(3, f"model is not ready yet ({code}): {message}. Retry shortly.")
        return _fail(3, f"invoke failed ({code}): {message}")

    elapsed_ms = (time.perf_counter() - started) * 1000
    content = response["output"]["message"]["content"]
    text = "".join(part.get("text", "") for part in content).strip()
    usage = response.get("usage", {})

    print(f"  reply     : {text!r}")
    print(f"  stop reason: {response.get('stopReason')}")
    print(f"  tokens    : {usage.get('inputTokens', 0)} in / {usage.get('outputTokens', 0)} out")
    print(f"  latency   : {elapsed_ms:.0f} ms")
    print("\nBedrock is ready for #22.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
