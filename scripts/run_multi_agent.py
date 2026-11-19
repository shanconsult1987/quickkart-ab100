import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.orchestrator import investigate_sync


def main():
    result = investigate_sync("QK-1002")

    print("\n========== AGENT EXECUTION ==========")

    for item in result["agents"]:
        print(f"\n--- {item['agent']} ---")
        print(item["response"])

    print("\n========== SUPERVISOR REPORT ==========")
    print(result["final_report"])

    output_path = "data/last_agent_run.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()