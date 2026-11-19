import json
import sys

from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.orchestrator import investigate_sync
from app.services.state import (
    create_session,
    add_step,
    complete_session,
)
from app.services.memory import remember, get_memory_context
from app.services.audit import write_audit
from app.services.guardrails import validate_order_id, validate_agent_output


def main():
    order_id = "QK-1002"

    validate_order_id(order_id)

    session_id = create_session(order_id)

    write_audit(
        "investigation_started",
        "WorkshopUser",
        {"order_id": order_id, "session_id": session_id},
    )

    result = investigate_sync(order_id)

    for agent_result in result["agents"]:
        validate_agent_output(agent_result["response"])

        add_step(
            session_id,
            agent_result["agent"],
            "completed",
            agent_result["response"][:500],
        )

    remember(
        order_id,
        "Multi-agent investigation completed. "
        + result["final_report"][:500],
    )

    completed = complete_session(session_id)

    write_audit(
        "investigation_completed",
        "QuickKartSupervisor",
        {
            "order_id": order_id,
            "session_id": session_id,
        },
    )

    print("\n========== FINAL REPORT ==========")
    print(result["final_report"])

    print("\n========== SESSION ==========")
    print(json.dumps(completed, indent=2))

    print("\n========== MEMORY ==========")
    print(get_memory_context(order_id))

    print("\nDay 2 demonstration completed.")


if __name__ == "__main__":
    main()