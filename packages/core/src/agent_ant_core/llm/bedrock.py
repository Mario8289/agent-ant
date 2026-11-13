"""Bedrock adapter for the ``LLM`` seam (D-009, D-015).

Uses the Converse API so one call shape works across model families, which keeps the
``LLM_MODEL`` swap in ``.env`` a config change. Credentials come from the named AWS profile
(``Settings.aws_profile``), never from keys in ``.env``: boto3 reads only the real environment,
and ``~/.aws/credentials`` keeps the secret out of the project directory.
"""

from typing import Any, Protocol, cast

import boto3  # pyright: ignore[reportMissingTypeStubs]

# Extraction output is a small JSON object; the cap bounds cost if a model rambles.
MAX_TOKENS = 1024


class Converser(Protocol):
    """The slice of the boto3 ``bedrock-runtime`` client this adapter uses (boto3 is untyped)."""

    def converse(self, **kwargs: Any) -> dict[str, Any]: ...


class BedrockLLM:
    """Satisfies ``LLM`` by sending the prompt to a Bedrock model and returning its text."""

    def __init__(
        self,
        model_id: str,
        region: str,
        profile: str | None = None,
        client: Converser | None = None,
    ) -> None:
        if model_id.startswith("global."):
            # global.* can route outside the EU, which D-015 rejects.
            raise ValueError(f"{model_id} is a global profile; use an eu.* profile (D-015)")
        self.model_id = model_id
        if client is None:
            session = boto3.Session(profile_name=profile, region_name=region)  # pyright: ignore[reportUnknownMemberType]
            client = cast("Converser", session.client("bedrock-runtime"))  # pyright: ignore[reportUnknownMemberType]
        self._client = client

    def complete(self, prompt: str) -> str:
        # temperature 0: extraction should be repeatable, and the eval compares runs.
        response = self._client.converse(
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS, "temperature": 0},
        )
        parts: list[dict[str, Any]] = response["output"]["message"]["content"]
        return "".join(part.get("text", "") for part in parts)
