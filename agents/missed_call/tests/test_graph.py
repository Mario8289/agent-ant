"""Tests for the missed-call graph: branching and resume (issue #23).

Uses ``MemorySaver`` so a run can pause and resume without Postgres; the checkpointer is an
injected dependency, so swapping in ``PostgresSaver`` later changes nothing here.
"""

import json
import uuid
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from agent_ant_core.testing import FakeLLM
from agent_ant_missed_call.graph import build_agent, build_graph

MESSAGE = "hi its Sam, boiler has packed in, Leeds LS6, urgent"
GOOD = json.dumps(
    {"name": "Sam", "job_type": "boiler repair", "location": "Leeds LS6", "urgency": "high"}
)
BAD = json.dumps({"urgency": "ASAP!!"})


def _good_fragment() -> dict[str, Any]:
    return {
        "job": {"name": "Sam", "job_type": "boiler repair", "location": "Leeds LS6"},
        "validated": True,
        "prompt_version": "extract_v1",
        "repair_attempts": 0,
        "raw_outputs": [GOOD],
        "last_error": None,
    }


def _bad_fragment() -> dict[str, Any]:
    return {
        "job": None,
        "validated": False,
        "prompt_version": "extract_v1",
        "repair_attempts": 2,
        "raw_outputs": [BAD],
        "last_error": "- urgency: Input should be 'low', 'medium', 'high' or 'unknown'",
    }


class CountingExtractor:
    """Fake extractor that records calls, to prove completed nodes are not re-run."""

    def __init__(self, fragment: dict[str, Any]) -> None:
        self.fragment = fragment
        self.calls = 0

    def __call__(self, message: str) -> dict[str, Any]:
        self.calls += 1
        return self.fragment


def _config() -> dict[str, Any]:
    # A new thread per test keeps runs isolated without clearing any checkpoint tables.
    return {"configurable": {"thread_id": f"test-{uuid.uuid4()}"}}


def test_valid_message_pauses_at_the_interrupt() -> None:
    graph = build_graph(CountingExtractor(_good_fragment()), MemorySaver())
    result = graph.invoke({"message": MESSAGE}, _config())

    assert result["__interrupt__"][0].value["job"]["job_type"] == "boiler repair"
    assert result.get("status") == "captured"  # not approved until a human says so


def test_approve_resumes_to_approved() -> None:
    graph = build_graph(CountingExtractor(_good_fragment()), MemorySaver())
    config = _config()
    graph.invoke({"message": MESSAGE}, config)
    result = graph.invoke(Command(resume={"action": "approve"}), config)

    assert result["status"] == "approved"
    assert graph.get_state(config).next == ()


def test_reject_resumes_to_rejected() -> None:
    graph = build_graph(CountingExtractor(_good_fragment()), MemorySaver())
    config = _config()
    graph.invoke({"message": MESSAGE}, config)
    result = graph.invoke(Command(resume={"action": "reject"}), config)

    assert result["status"] == "rejected"


def test_invalid_extraction_branches_past_the_interrupt() -> None:
    graph = build_graph(CountingExtractor(_bad_fragment()), MemorySaver())
    result = graph.invoke({"message": MESSAGE}, _config())

    assert "__interrupt__" not in result
    assert result["status"] == "needs_review"
    assert result["job"] is None


def test_resume_survives_a_restart() -> None:
    # Pause in one "process", then resume from a fresh graph over the same checkpointer.
    first = CountingExtractor(_good_fragment())
    checkpointer = MemorySaver()
    config = _config()
    build_graph(first, checkpointer).invoke({"message": MESSAGE}, config)

    second = CountingExtractor(_good_fragment())
    graph = build_graph(second, checkpointer)
    result = graph.invoke(Command(resume={"action": "approve"}), config)

    assert result["status"] == "approved"
    assert first.calls == 1
    assert second.calls == 0  # extract was checkpointed, not re-run


def test_build_agent_wires_the_fake_provider_to_the_interrupt() -> None:
    llm = FakeLLM(GOOD)
    graph = build_agent(llm, MemorySaver())
    result = graph.invoke({"message": MESSAGE}, _config())

    assert result["__interrupt__"][0].value["job"]["job_type"] == "boiler repair"
    assert result["status"] == "captured"
    assert len(llm.prompts) == 1


def test_build_agent_routes_unrecoverable_output_to_needs_review() -> None:
    # The fake never produces valid JSON, so repair is exhausted and a human must step in.
    llm = FakeLLM(*["not json"] * 10)
    graph = build_agent(llm, MemorySaver())
    result = graph.invoke({"message": MESSAGE}, _config())

    assert "__interrupt__" not in result
    assert result["status"] == "needs_review"
    assert result["repair_attempts"] == 2
    assert len(llm.prompts) == 3
