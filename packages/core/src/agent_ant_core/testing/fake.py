"""A scripted LLM for tests and scaffolding (before any provider is chosen)."""


class FakeLLM:
    """Returns queued replies in order and records every prompt it was given.

    Implements the ``LLM`` protocol from ``agent_ant_core.llm`` structurally — no import needed,
    so it can also stand in for a provider that is not installed yet.
    """

    def __init__(self, *replies: str) -> None:
        self.replies = list(replies)
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.replies.pop(0)
