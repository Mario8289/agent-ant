"""Build a provider from settings (D-009).

The Bedrock adapter that satisfies ``LLM`` is written once the credentials checklist in
``docs/10`` is done (D-009). Until then this returns ``None``, so any caller that needs a real
provider (the app's background task, the eval harness) skips rather than failing.
"""

from agent_ant_core.config import Settings
from agent_ant_core.llm.client import LLM


def build_llm(settings: Settings) -> LLM | None:
    """Return the configured provider, or None when none is ready.

    The single seam every provider-dependent caller uses. Today no adapter exists, so this is
    always None; when the Bedrock adapter lands it becomes a real constructor keyed off
    ``settings.llm_provider`` / ``settings.llm_model``.
    """
    return None  # TODO(#22 real call): return a Bedrock-backed LLM when llm_provider is set.
