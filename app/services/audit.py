import json
from datetime import datetime, timezone
from uuid import uuid4

from app.config import AUDIT_DIR


AUDIT_FILE = AUDIT_DIR / "events.jsonl"


def write_audit(event_type, actor, details):
    event = {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "actor": actor,
        "details": details,
    }

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")

    return event