import json
from datetime import datetime, timezone

from app.config import MEMORY_DIR


def memory_path(order_id):
    safe_id = "".join(
        character for character in order_id
        if character.isalnum() or character in "-_"
    )

    return MEMORY_DIR / f"{safe_id}.json"


def read_memory(order_id):
    path = memory_path(order_id)

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def remember(order_id, note):
    if not isinstance(note, str) or not note.strip():
        raise ValueError("Memory note cannot be empty.")

    history = read_memory(order_id)

    history.append({
        "note": note.strip(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    memory_path(order_id).write_text(
        json.dumps(history, indent=2),
        encoding="utf-8",
    )

    return history


def get_memory_context(order_id):
    history = read_memory(order_id)

    if not history:
        return "No previous investigation memory."

    return "\n".join(
        item["note"] for item in history[-5:]
    )