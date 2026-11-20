
import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.orchestrator import investigate_sync
from app.services.evaluation import (
    evaluate_all,
    load_cases,
    save_results
)


def run_single_order(order_id):

    print()
    print("=" * 60)
    print(f"Running investigation for {order_id}")
    print("=" * 60)

    investigation = investigate_sync(order_id)

    report = investigation["final_report"]

    print()
    print("ACTUAL SUPERVISOR REPORT")
    print("-" * 60)
    print(report)

    return report


def main():

    parser = argparse.ArgumentParser(
        description="Evaluate actual QuickKart agent investigations."
    )

    parser.add_argument(
        "--order",
        help="Evaluate one order, for example QK-1002."
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Evaluate all five seeded orders."
    )

    args = parser.parse_args()

    if not args.order and not args.all:

        parser.error(
            "Specify --order QK-1002 or --all."
        )

    cases = load_cases()

    if args.order:

        matching_cases = [
            case
            for case in cases
            if case["order_id"] == args.order
        ]

        if not matching_cases:

            raise SystemExit(
                f"No evaluation case exists for {args.order}."
            )

    else:

        matching_cases = cases

    actual_reports = {}

    for case in matching_cases:

        order_id = case["order_id"]

        actual_reports[order_id] = run_single_order(
            order_id
        )

    result = evaluate_all(actual_reports)

    result["execution_mode"] = (
        "single_order"
        if args.order
        else "all_orders"
    )

    save_results(result)

    print()
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2
        )
    )

    print()
    print(
        f"Passed: {result['passed']} / {result['total']}"
    )

    print(
        f"Failed: {result['failed']}"
    )

    print(
        f"Pass rate: {result['pass_rate']}%"
    )

    print()
    print(
        "Results saved to data/evaluations/latest.json"
    )

    if result["failed"] > 0:

        print(
            "One or more evaluation cases failed."
        )


if __name__ == "__main__":

    main()
