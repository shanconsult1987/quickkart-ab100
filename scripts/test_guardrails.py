import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.guardrails import (
    validate_order_id,
    check_action,
)

from app.services.approval import (
    request_approval,
    decide_approval,
)


def main():
    print("Validating order ID...")
    validate_order_id("QK-1002")

    print("Checking refund guardrail...")
    result = check_action("execute_refund")
    print(result)

    if result["requires_approval"]:
        request = request_approval(
            "QK-1002",
            "execute_refund",
            "Customer requested a refund due to order delay.",
        )

        print("\nApproval request created:")
        print(request)

        decision = decide_approval(
            request["approval_id"],
            "rejected",
            "WorkshopApprover",
        )

        print("\nApproval decision:")
        print(decision)


if __name__ == "__main__":
    main()