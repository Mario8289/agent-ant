"""The LLM provider seam (D-009).

One method is the whole contract: ``complete(prompt) -> str``. Every provider adapter — Bedrock
first, and any future OpenAI-style API — satisfies this Protocol, so the rest of the code never
knows which provider it is talking to. A ``FakeLLM`` lives in ``agent_ant_core.testing`` for
tests and scaffolding before credentials exist.
"""

from typing import Protocol


class LLM(Protocol):
    """A provider that turns a prompt into text.

    Deliberately minimal: the extraction loop and the graph depend only on this, so swapping
    providers (D-009) is a config change, not a rewrite. Nothing here writes to customers;
    LLM output goes to the tradesperson only (D-004).
    """

    def complete(self, prompt: str) -> str: ...
