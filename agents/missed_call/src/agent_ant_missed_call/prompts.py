"""Versioned prompt loading (issue #23).

Prompts are files, never inline strings (AGENTS.md). When a prompt changes in a way that can
change output, bump the version and record it in the audit row (``prompt_version``) so accuracy
changes can be attributed.
"""

from importlib.resources import files

EXTRACT_PROMPT_VERSION = "extract_v3"
REPAIR_PROMPT_VERSION = "repair_v1"

_PACKAGE = "agent_ant_missed_call"


def load_prompt(name: str) -> str:
    """Return the prompt text for ``name`` (a version tag like ``extract_v1``)."""
    return files(_PACKAGE).joinpath("prompts", f"{name}.md").read_text()
