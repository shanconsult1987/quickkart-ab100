
import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock


ROOT = Path(__file__).resolve().parents[2]

LOG_FILE = ROOT / "data" / "telemetry.jsonl"

TELEMETRY_LOCK = Lock()


def record_event(event_type, **details):

    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    event = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "event_type": event_type,

        **details
    }

    with TELEMETRY_LOCK:

        with LOG_FILE.open(
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(
                    event,
                    default=str
                ) + "\n"
            )

    return event


def record_http(
    method,
    path,
    status_code,
    latency_ms
):

    return record_event(
        "http",

        method=method,

        path=path,

        status_code=int(status_code),

        latency_ms=round(
            float(latency_ms),
            2
        )
    )


def record_model(
    model,
    operation,
    latency_ms,
    usage=None
):

    usage = usage or {}

    return record_event(
        "model",

        model=model,

        operation=operation,

        latency_ms=round(
            float(latency_ms),
            2
        ),

        input_tokens=int(
            usage.get("input_tokens", 0) or 0
        ),

        output_tokens=int(
            usage.get("output_tokens", 0) or 0
        ),

        total_tokens=int(
            usage.get("total_tokens", 0) or 0
        )
    )


def record_agent(
    agent_name,
    latency_ms,
    status="success"
):

    return record_event(
        "agent",

        agent=agent_name,

        latency_ms=round(
            float(latency_ms),
            2
        ),

        status=status
    )
