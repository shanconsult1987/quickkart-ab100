import json
from datetime import datetime, timezone
from uuid import uuid4

from app.config import DATA_DIR
from app.services.audit import write_audit


APPROVAL_FILE = DATA_DIR / "approval_requests.json"


def load_approvals():
    if not APPROVAL_FILE.exists():
        return []

    with APPROVAL_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def request_approval(order_id, action, reason):
    records = load_approvals()

    request = {
        "approval_id": str(uuid4()),
        "order_id": order_id,
        "action": action,
        "reason": reason,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    records.append(request)

    APPROVAL_FILE.write_text(
        json.dumps(records, indent=2),
        encoding="utf-8",
    )

    write_audit(
        "approval_requested",
        "QuickKartAgent",
        request,
    )

    return request


def decide_approval(approval_id, decision, approver):
    if decision not in ["approved", "rejected"]:
        raise ValueError("Decision must be approved or rejected.")

    records = load_approvals()

    for record in records:
        if record["approval_id"] == approval_id:
            if record["status"] != "pending":
                raise ValueError("Approval has already been decided.")

            record["status"] = decision
            record["approver"] = approver
            record["decision_at"] = datetime.now(
                timezone.utc
            ).isoformat()

            APPROVAL_FILE.write_text(
                json.dumps(records, indent=2),
                encoding="utf-8",
            )

            write_audit(
                "approval_decided",
                approver,
                record,
            )

            return record

    raise ValueError("Approval request not found.")