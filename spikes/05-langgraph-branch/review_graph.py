"""#61 Spike 5: extract -> validate -> (branch) -> interrupt for approval -> resume.

The graph mirrors the shape in docs/05 and ADR 0001:

    extract -> validate --valid--> human_review (interrupt) --> END (approved / rejected)
                        \\--invalid--> flag_for_human --------> END (needs_review)

`interrupt()` pauses the run and saves state through the checkpointer, so the tradesperson
can answer minutes or days later, from a different process. Human approval is required before
a job counts as confirmed (rule 6), so the only path to "approved" runs through the interrupt.

Extraction is injected as a plain function so the graph is testable with no LLM. That also
matches the ADR: nodes call plain functions and business logic stays unit-testable.

LangGraph caveat that shapes the code: when a run resumes, the interrupted node re-executes
from its first line. Anything before `interrupt()` in that node must be safe to repeat, which
is why `human_review` does no side effects before it. Completed nodes (extract, validate) are
not re-run.
"""

from collections.abc import Callable
from typing import Any, Literal, TypedDict

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from pydantic import BaseModel, ConfigDict, ValidationError

Status = Literal["captured", "needs_review", "approved", "rejected"]
ExtractFn = Callable[[str], dict[str, Any]]


class JobExtraction(BaseModel):
    """Trimmed copy of spike 04's model, so each spike stands alone."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    job_type: str | None = None
    location: str | None = None
    urgency: Literal["low", "medium", "high", "unknown"] = "unknown"
    preferred_date: str | None = None


class State(TypedDict, total=False):
    message: str
    raw: dict[str, Any]
    job: dict[str, Any] | None
    error: str | None
    status: Status


def build_graph(extract_fn: ExtractFn, checkpointer: BaseCheckpointSaver[Any]) -> Any:
    def extract(state: State) -> State:
        return {"raw": extract_fn(state["message"])}

    def validate(state: State) -> State:
        try:
            job = JobExtraction.model_validate(state["raw"])
        except ValidationError as exc:
            return {"job": None, "error": f"{exc.error_count()} validation error(s)"}
        return {"job": job.model_dump(), "error": None, "status": "captured"}

    def route_after_validate(state: State) -> Literal["human_review", "flag_for_human"]:
        return "human_review" if state.get("job") is not None else "flag_for_human"

    def human_review(state: State) -> State:
        # Pauses here. On resume, interrupt() returns the value passed to Command(resume=...).
        decision = interrupt({"job": state["job"], "question": "Approve this job?"})
        return {"status": "approved" if decision.get("action") == "approve" else "rejected"}

    def flag_for_human(state: State) -> State:
        return {"status": "needs_review"}

    builder = StateGraph(State)
    builder.add_node("extract", extract)
    builder.add_node("validate", validate)
    builder.add_node("human_review", human_review)
    builder.add_node("flag_for_human", flag_for_human)

    builder.add_edge(START, "extract")
    builder.add_edge("extract", "validate")
    builder.add_conditional_edges("validate", route_after_validate)
    builder.add_edge("human_review", END)
    builder.add_edge("flag_for_human", END)

    return builder.compile(checkpointer=checkpointer)
