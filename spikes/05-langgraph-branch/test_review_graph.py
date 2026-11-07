import os
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import psycopg
import pytest
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command
from review_graph import build_graph

# Default matches this spike's docker-compose.yml (port 5434). The SQLAlchemy-style scheme
# used in .env.example is normalised because psycopg wants a plain "postgresql://".
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://agent_ant:agent_ant@localhost:5434/agent_ant"
).replace("postgresql+psycopg://", "postgresql://", 1)

MESSAGE = "hi its Sam, boiler has packed in, Leeds LS6, urgent"
GOOD = {"name": "Sam", "job_type": "boiler repair", "location": "Leeds LS6", "urgency": "high"}
BAD = {"urgency": "ASAP!!"}


class CountingExtractor:
    """Fake extractor that records calls, to prove completed nodes are not re-run."""

    def __init__(self, result: dict[str, Any]) -> None:
        self.result = result
        self.calls = 0

    def __call__(self, message: str) -> dict[str, Any]:
        self.calls += 1
        return self.result


@contextmanager
def saver() -> Iterator[PostgresSaver]:
    """A fresh checkpointer on its own connection, like a freshly started process."""
    try:
        with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
            checkpointer.setup()
            yield checkpointer
    except psycopg.OperationalError as exc:
        pytest.skip(f"Postgres not reachable at {DATABASE_URL.split('@')[-1]}: {exc}")


@pytest.fixture
def config() -> dict[str, Any]:
    # A new thread per test keeps runs isolated without clearing the checkpoint tables.
    return {"configurable": {"thread_id": f"test-{uuid.uuid4()}"}}


def test_valid_message_pauses_at_the_interrupt(config: dict[str, Any]) -> None:
    with saver() as checkpointer:
        graph = build_graph(CountingExtractor(GOOD), checkpointer)
        result = graph.invoke({"message": MESSAGE}, config)

        assert result["__interrupt__"][0].value["job"]["job_type"] == "boiler repair"
        assert graph.get_state(config).next == ("human_review",)
        assert result.get("status") == "captured"  # not approved until a human says so


def test_approve_resumes_to_approved(config: dict[str, Any]) -> None:
    with saver() as checkpointer:
        graph = build_graph(CountingExtractor(GOOD), checkpointer)
        graph.invoke({"message": MESSAGE}, config)
        result = graph.invoke(Command(resume={"action": "approve"}), config)

        assert result["status"] == "approved"
        assert graph.get_state(config).next == ()


def test_reject_resumes_to_rejected(config: dict[str, Any]) -> None:
    with saver() as checkpointer:
        graph = build_graph(CountingExtractor(GOOD), checkpointer)
        graph.invoke({"message": MESSAGE}, config)
        result = graph.invoke(Command(resume={"action": "reject"}), config)

        assert result["status"] == "rejected"


def test_invalid_extraction_branches_past_the_interrupt(config: dict[str, Any]) -> None:
    with saver() as checkpointer:
        graph = build_graph(CountingExtractor(BAD), checkpointer)
        result = graph.invoke({"message": MESSAGE}, config)

        assert "__interrupt__" not in result
        assert result["status"] == "needs_review"
        assert result["job"] is None
        assert graph.get_state(config).next == ()


def test_resume_survives_a_restart(config: dict[str, Any]) -> None:
    # Pause in one "process", then resume from a brand-new connection, saver and graph.
    first = CountingExtractor(GOOD)
    with saver() as checkpointer:
        build_graph(first, checkpointer).invoke({"message": MESSAGE}, config)

    second = CountingExtractor(GOOD)
    with saver() as checkpointer:
        graph = build_graph(second, checkpointer)
        assert graph.get_state(config).next == ("human_review",)
        result = graph.invoke(Command(resume={"action": "approve"}), config)

    assert result["status"] == "approved"
    assert first.calls == 1
    assert second.calls == 0  # extract was checkpointed, not re-run


def test_threads_are_isolated() -> None:
    a = {"configurable": {"thread_id": f"test-{uuid.uuid4()}"}}
    b = {"configurable": {"thread_id": f"test-{uuid.uuid4()}"}}
    with saver() as checkpointer:
        graph = build_graph(CountingExtractor(GOOD), checkpointer)
        graph.invoke({"message": MESSAGE}, a)
        graph.invoke({"message": MESSAGE}, b)
        graph.invoke(Command(resume={"action": "approve"}), a)

        assert graph.get_state(a).next == ()
        assert graph.get_state(b).next == ("human_review",)
