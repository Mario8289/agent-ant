"""Build a provider from settings (D-009).

The single seam every provider-dependent caller uses (the app's background task, the eval
harness). Returning ``None`` when nothing is configured lets those callers skip rather than
fail, so a fresh checkout without credentials still runs the unit tests.
"""

from agent_ant_core.config import Settings
from agent_ant_core.llm.bedrock import BedrockLLM
from agent_ant_core.llm.client import LLM


def build_llm(settings: Settings) -> LLM | None:
    """Return the configured provider, or None when none is ready.

    Needs ``LLM_PROVIDER`` and ``LLM_MODEL``. An unknown provider is an error rather than
    None: a typo should not silently turn extraction off.
    """
    if not settings.llm_provider or not settings.llm_model:
        return None
    if settings.llm_provider == "bedrock":
        return BedrockLLM(
            model_id=settings.llm_model,
            region=settings.aws_region,
            profile=settings.aws_profile,
        )
    raise ValueError(f"unknown LLM_PROVIDER {settings.llm_provider!r}; only 'bedrock' exists")
