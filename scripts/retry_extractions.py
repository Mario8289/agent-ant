"""Re-run extraction over retryable replies and dead-letter the exhausted (#34).

Run manually or on a schedule (``just retry-extractions``). A reply whose extraction failed or
never ran — a crash between the webhook commit and the background task, or a provider outage —
is re-extracted up to ``MAX_EXTRACTION_ATTEMPTS`` times. The ones that still fail are promoted
to ``status='dead'`` and shown on the dashboard's failure panel.
"""

import sys

from agent_ant_api.extraction import retry_failed_extractions
from agent_ant_core.config import get_settings
from agent_ant_core.db.session import get_sessionmaker
from agent_ant_core.llm import build_llm


def main() -> int:
    settings = get_settings()
    llm = build_llm(settings)
    if llm is None:
        print("No LLM configured; nothing to retry.", file=sys.stderr)
        return 2

    with get_sessionmaker()() as session:
        recovered = retry_failed_extractions(session, llm, settings.llm_model or "unconfigured")

    print(f"recovered {recovered} job(s); the rest were left failed or dead-lettered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
