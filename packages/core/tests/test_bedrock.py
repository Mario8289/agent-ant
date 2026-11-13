"""Tests for the Bedrock adapter and the provider seam (issues #22, #27)."""

from typing import Any

import pytest

from agent_ant_core.config import Settings
from agent_ant_core.llm import build_llm
from agent_ant_core.llm.bedrock import BedrockLLM


class FakeRuntime:
    """Stands in for the boto3 bedrock-runtime client and records the request."""

    def __init__(self, parts: list[dict[str, str]]) -> None:
        self.parts = parts
        self.request: dict[str, Any] = {}

    def converse(self, **kwargs: Any) -> dict[str, Any]:
        self.request = kwargs
        return {"output": {"message": {"content": self.parts}}}


def test_complete_sends_the_prompt_and_joins_text_parts() -> None:
    runtime = FakeRuntime([{"text": '{"a": '}, {"text": "1}"}])
    llm = BedrockLLM("eu.anthropic.test", "eu-west-2", client=runtime)

    assert llm.complete("hello") == '{"a": 1}'
    assert runtime.request["modelId"] == "eu.anthropic.test"
    assert runtime.request["messages"][0]["content"] == [{"text": "hello"}]
    assert runtime.request["inferenceConfig"]["temperature"] == 0


def test_global_profiles_are_rejected() -> None:
    with pytest.raises(ValueError, match="global"):
        BedrockLLM("global.anthropic.test", "eu-west-2", client=FakeRuntime([]))


def _settings(**values: str) -> Settings:
    return Settings(_env_file=None, **values)  # type: ignore[call-arg, arg-type]


def test_build_llm_is_none_without_provider_and_model() -> None:
    assert build_llm(_settings()) is None
    assert build_llm(_settings(llm_provider="bedrock")) is None


def test_build_llm_rejects_an_unknown_provider() -> None:
    with pytest.raises(ValueError, match="bedrok"):
        build_llm(_settings(llm_provider="bedrok", llm_model="m"))
