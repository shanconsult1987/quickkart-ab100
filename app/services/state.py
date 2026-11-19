import json
from datetime import datetime, timezone
from uuid import uuid4

from app.config import DATA_DIR


STATE_FILE = DATA_DIR / "agent_state.json"


def load_state():
    if not STATE_FILE.exists():
        return {"sessions": {}}

    with STATE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_state(state):
    STATE_FILE.write_text(
        json.dumps(state, indent=2),
        encoding="utf-8",
    )


def create_session(order_id):
    state = load_state()

    session_id = str(uuid4())

    state["sessions"][session_id] = {
        "order_id": order_id,
        "status": "started",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "steps": [],
    }

    save_state(state)

    return session_id


def add_step(session_id, agent_name, status, summary):
    state = load_state()

    if session_id not in state["sessions"]:
        raise ValueError("Session not found.")

    state["sessions"][session_id]["steps"].append({
        "agent": agent_name,
        "status": status,
        "summary": summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    save_state(state)


def complete_session(session_id):
    state = load_state()

    if session_id not in state["sessions"]:
        raise ValueError("Session not found.")

    state["sessions"][session_id]["status"] = "completed"

    save_state(state)

    return state["sessions"][session_id]