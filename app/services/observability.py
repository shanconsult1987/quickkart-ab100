
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

LOG_FILE = ROOT / "data" / "telemetry.jsonl"


def load_events():

    if not LOG_FILE.exists():

        return []

    events = []

    with LOG_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            try:

                events.append(
                    json.loads(line)
                )

            except json.JSONDecodeError:

                continue

    return events


def percentile(values, percentage):

    if not values:

        return 0

    ordered = sorted(values)

    index = max(
        0,
        math.ceil(
            percentage / 100 * len(ordered)
        ) - 1
    )

    return round(
        ordered[index],
        2
    )


def get_metrics():

    events = load_events()

    http_events = [
        event
        for event in events
        if event.get("event_type") == "http"
    ]

    model_events = [
        event
        for event in events
        if event.get("event_type") == "model"
    ]

    agent_events = [
        event
        for event in events
        if event.get("event_type") == "agent"
    ]

    latencies = [
        float(event.get("latency_ms", 0))
        for event in http_events
    ]

    statuses = Counter(
        str(event.get("status_code", 0))
        for event in http_events
    )

    input_tokens = sum(
        int(event.get("input_tokens", 0))
        for event in model_events
    )

    output_tokens = sum(
        int(event.get("output_tokens", 0))
        for event in model_events
    )

    total_requests = len(http_events)

    successful_requests = sum(
        count
        for status, count in statuses.items()
        if status.startswith("2")
    )

    client_errors = sum(
        count
        for status, count in statuses.items()
        if status.startswith("4")
    )

    server_errors = sum(
        count
        for status, count in statuses.items()
        if status.startswith("5")
    )

    average_latency = (
        round(
            sum(latencies) / len(latencies),
            2
        )
        if latencies
        else 0
    )

    failed_agents = sum(
        1
        for event in agent_events
        if event.get("status") != "success"
    )

    return {

        "http": {

            "total_requests": total_requests,

            "success_2xx": successful_requests,

            "client_errors_4xx": client_errors,

            "server_errors_5xx": server_errors,

            "average_latency_ms": average_latency,

            "p95_latency_ms": percentile(
                latencies,
                95
            )
        },

        "models": {

            "calls": len(model_events),

            "input_tokens": input_tokens,

            "output_tokens": output_tokens,

            "total_tokens": (
                input_tokens + output_tokens
            )
        },

        "agents": {

            "calls": len(agent_events),

            "failures": failed_agents
        },

        "event_count": len(events)
    }
