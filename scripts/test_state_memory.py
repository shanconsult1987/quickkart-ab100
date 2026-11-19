import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.state import (
    create_session,
    add_step,
    complete_session,
)

from app.services.memory import (
    remember,
    get_memory_context,
)


def main():
    session_id = create_session("QK-1002")

    add_step(
        session_id,
        "PlannerAgent",
        "completed",
        "Identified pending payment as an investigation area.",
    )

    add_step(
        session_id,
        "PaymentAgent",
        "completed",
        "Payment status is pending.",
    )

    session = complete_session(session_id)

    remember(
        "QK-1002",
        "Previous investigation found a pending payment.",
    )

    print("\nSESSION")
    print(session)

    print("\nMEMORY")
    print(get_memory_context("QK-1002"))


if __name__ == "__main__":
    main()