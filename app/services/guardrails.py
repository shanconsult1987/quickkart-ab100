import re


BLOCKED_ACTIONS = [
    "execute_refund",
    "issue_refund",
    "cancel_order",
    "update_payment",
    "modify_inventory",
    "delete_order",
]


def validate_order_id(order_id):
    if not isinstance(order_id, str):
        raise ValueError("Order ID must be text.")

    if not re.fullmatch(r"QK-[0-9]{4}", order_id):
        raise ValueError("Invalid QuickKart order ID.")

    return True


def validate_agent_output(output):
    if not isinstance(output, str):
        raise ValueError("Agent output must be text.")

    if len(output) > 12000:
        raise ValueError("Agent output exceeds the allowed length.")

    return True


def check_action(action):
    normalized = str(action).lower().strip()

    if normalized in BLOCKED_ACTIONS:
        return {
            "allowed": False,
            "requires_approval": True,
            "reason": "Financial or operational mutation is not permitted.",
        }

    return {
        "allowed": True,
        "requires_approval": False,
        "reason": "Read-only action permitted.",
    }