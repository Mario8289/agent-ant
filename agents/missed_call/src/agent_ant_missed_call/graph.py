"""The missed-call extraction graph (D-008, issue #23).

    extract -> route --job-->     human_review (interrupt) --> END (approved / rejected)
                     \\--no job--> flag_for_human -----------> END (needs_review)

The graph is orchestration only: extraction is injected as a plain function, so the graph is
unit-testable with no LLM and no provider chosen yet — matching the ADR that nodes call plain
functions and ``packages/core`` stays framework-free. ``build_agent`` wires the real
``extract_job`` from core plus the versioned prompts.

Human approval is required before a job counts as confirmed (rule 6), so the only path to
"approved" runs through the interrupt. LangGraph re-executes an interrupted node from its first
line on resume, so ``human_review`` performs no side effects before ``interrupt()``.
"""

from collections.abc import Callable
from typing import Any, Literal, NotRequired, Required, TypedDict

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from agent_ant_core.llm import LLM, extract_job
from agent_ant_missed_call.prompts import (
    EXTRACT_PROMPT_VERSION,
    REPAIR_PROMPT_VERSION,
    load_prompt,
)

Status = Literal["captured", "needs_review", "approved", "rejected"]

# An extractor turns the message into the state fragment the graph records: the validated job
# (or None) plus the audit fields (prompt_version, repair_attempts, raw_outputs, last_error).
ExtractFn = Callable[[str], dict[str, Any]]


class State(TypedDict, total=False):
    message: Required[str]
    job: NotRequired[dict[str, Any] | None]
    validated: NotRequired[bool]
    prompt_version: NotRequired[str]
    repair_attempts: NotRequired[int]
    raw_outputs: NotRequired[list[str]]
    last_error: NotRequired[str | None]
    status: NotRequired[Status]


def build_graph(extract_fn: ExtractFn, checkpointer: BaseCheckpointSaver[Any]) -> Any:
    """Build the compiled graph.

    ``extract_fn`` is a plain function ``message -> state fragment``; tests inject a fake so the
    graph's branching and resume behaviour are proven with no provider. The checkpointer is what
    lets a run pause at the interrupt and resume later, possibly from another process.
    """

    def extract(state: State) -> dict[str, Any]:
        fragment = extract_fn(state["message"])
        # A valid extraction is "captured" and waits for a human; a failed one is already
        # "needs_review". Setting it here means the status is correct while paused at the
        # interrupt, not only after the human answers.
        fragment["status"] = "captured" if fragment.get("job") is not None else "needs_review"
        return fragment

    def route(state: State) -> Literal["human_review", "flag_for_human"]:
        return "human_review" if state.get("job") is not None else "flag_for_human"

    def human_review(state: State) -> dict[str, Status]:
        # Pauses here. On resume, interrupt() returns the value passed to Command(resume=...).
        decision = interrupt({"job": state.get("job"), "question": "Approve this job?"})
        return {"status": "approved" if decision.get("action") == "approve" else "rejected"}

    def flag_for_human(state: State) -> dict[str, Status]:
        return {"status": "needs_review"}

    builder = StateGraph(State)
    builder.add_node("extract", extract)
    builder.add_node("human_review", human_review)
    builder.add_node("flag_for_human", flag_for_human)

    builder.add_edge(START, "extract")
    builder.add_conditional_edges("extract", route)
    builder.add_edge("human_review", END)
    builder.add_edge("flag_for_human", END)

    return builder.compile(checkpointer=checkpointer)


def build_agent(
    llm: LLM,
    checkpointer: BaseCheckpointSaver[Any],
    *,
    max_repairs: int = 2,
) -> Any:
    """Wire the real extractor (core's ``extract_job`` + versioned prompts) into the graph.

    Returns a compiled graph that talks to ``llm`` and pauses for approval. Kept separate from
    ``build_graph`` so the graph itself stays testable with no provider.
    """
    extract_prompt = load_prompt(EXTRACT_PROMPT_VERSION)
    repair_prompt = load_prompt(REPAIR_PROMPT_VERSION)

    def extract_fn(message: str) -> dict[str, Any]:
        result = extract_job(
            llm,
            message,
            extract_prompt=extract_prompt,
            repair_prompt=repair_prompt,
            prompt_version=EXTRACT_PROMPT_VERSION,
            max_repairs=max_repairs,
        )
        return {
            "job": result.job.model_dump() if result.job else None,
            "validated": result.validated,
            "prompt_version": result.prompt_version,
            "repair_attempts": result.repair_attempts,
            "raw_outputs": result.raw_outputs,
            "last_error": result.last_error,
        }

    return build_graph(extract_fn, checkpointer)
