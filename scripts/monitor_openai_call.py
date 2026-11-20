import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.openai_agent import investigate_order

from app.business import get_order_context


def main():

    order_id = "QK-1002"

    order = get_order_context(
        order_id
    )

    print()
    print("=" * 55)
    print("QUICKKART OPENAI SDK MONITORING DEMO")
    print("=" * 55)

    result = investigate_order(
        order
    )

    print()
    print("MODEL")
    print(result["model"])

    print()
    print("RESPONSE ID")
    print(result["response_id"])

    print()
    print("TOKEN USAGE")

    print(
        "Input tokens:",
        result["usage"]["input_tokens"]
    )

    print(
        "Output tokens:",
        result["usage"]["output_tokens"]
    )

    print(
        "Total tokens:",
        result["usage"]["total_tokens"]
    )

    print()
    print("ACTUAL MODEL RESPONSE")
    print("-" * 55)

    print(
        result["response"]
    )


if __name__ == "__main__":

    main()
