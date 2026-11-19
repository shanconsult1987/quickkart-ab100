import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.openai_agent import investigate_order
from app.business import get_order_context


def main():
    order = get_order_context("QK-1002")

    result = investigate_order(order)

    print("\n--- QUICKKART AI INVESTIGATION ---")
    print(result["response"])

    print("\n--- MODEL USAGE ---")
    print(result["usage"])

    print("\nResponse ID:", result["response_id"])


if __name__ == "__main__":
    main()