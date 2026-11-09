"""The ``missed_call`` agent: turn a caller's reply into a structured job record.

Extraction lives in ``agent_ant_core.llm`` (#22); orchestration lives in ``graph.py`` (#23).
The agent never sends free-text messages to customers (decision D-004).
"""

__version__ = "0.1.0"
