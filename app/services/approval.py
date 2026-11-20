
import json
from datetime import datetime, timezone
from uuid import uuid4

from app.config import DATA_DIR

from app.services.audit import write_audit


APPROVAL_FILE = DATA_DIR / "approval_requests.json"


def load_approvals():

    if not APPROVAL_FILE.exists():

        return []

    with APPROVAL_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_approvals(records):

    APPROVAL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with APPROVAL_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2
        )


def request_approval(
    order_id,
    action,
    reason,
    investigation_id=None
):

    if not order_id:
        raise ValueError("Order ID is required.")

    if not action:
        raise ValueError("Action is required.")

    if not reason or not reason.strip():
        raise ValueError("Approval reason is required.")

    records = load_approvals()

    request = {

        "approval_id": str(uuid4()),

        "investigation_id": investigation_id,

        "order_id": order_id,

        "action": action,

        "reason": reason.strip(),

        "status": "pending",

        "created_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    records.append(request)

    save_approvals(records)

    write_audit(
        "approval_requested",
        "QuickKartAgent",
        request
    )

    return request


def decide_approval(
    approval_id,
    decision,
    approver,
    comment="Workshop decision recorded."
):

    if decision not in ["approved", "rejected"]:

        raise ValueError(
            "Decision must be approved or rejected."
        )

    if not approver or not approver.strip():

        raise ValueError(
            "Reviewer name is required."
        )

    if not comment or not comment.strip():

        raise ValueError(
            "Reviewer comment is required."
        )

    records = load_approvals()

    for record in records:

        if record["approval_id"] == approval_id:

            if record["status"] != "pending":

                raise ValueError(
                    "Approval has already been decided."
                )

            record["status"] = decision

            record["approver"] = approver.strip()

            record["comment"] = comment.strip()

            record["decision_at"] = datetime.now(
                timezone.utc
            ).isoformat()

            save_approvals(records)

            write_audit(
                "approval_decided",
                approver.strip(),
                record
            )

            return record

    raise ValueError(
        "Approval request not found."
    )
