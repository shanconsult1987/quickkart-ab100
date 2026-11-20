
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

EVALUATION_DIR = ROOT / "data" / "evaluations"

CASES_FILE = EVALUATION_DIR / "cases.csv"

RESULTS_FILE = EVALUATION_DIR / "latest.json"


def load_cases():
    if not CASES_FILE.exists():
        raise FileNotFoundError(
            f"Evaluation cases not found: {CASES_FILE}"
        )

    with CASES_FILE.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        return list(csv.DictReader(file))


def evaluate_report(case, report):

    report_text = str(report).lower()

    required_terms = [
        term.strip().lower()
        for term in case["required_terms"].split(";")
        if term.strip()
    ]

    forbidden_terms = [
        term.strip().lower()
        for term in case["forbidden_terms"].split(";")
        if term.strip()
    ]

    missing_terms = [
        term
        for term in required_terms
        if term not in report_text
    ]

    forbidden_found = [
        term
        for term in forbidden_terms
        if term in report_text
    ]

    passed = (
        len(missing_terms) == 0
        and len(forbidden_found) == 0
    )

    return {
        "case_id": case["case_id"],
        "order_id": case["order_id"],
        "passed": passed,
        "missing_terms": missing_terms,
        "forbidden_terms_found": forbidden_found
    }


def evaluate_all(reports):

    cases = load_cases()

    results = []

    for case in cases:

        order_id = case["order_id"]

        report = reports.get(order_id)

        if report is None:

            results.append({
                "case_id": case["case_id"],
                "order_id": order_id,
                "passed": False,
                "missing_terms": [],
                "forbidden_terms_found": [],
                "error": "No actual investigation report supplied."
            })

            continue

        result = evaluate_report(
            case,
            report
        )

        results.append(result)

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    failed = total - passed

    pass_rate = (
        round((passed / total) * 100, 2)
        if total > 0
        else 0
    )

    return {
        "evaluation_type": "keyword_and_policy_check",
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "results": results
    }


def save_results(result):

    EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with RESULTS_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=2
        )


def load_latest_results():

    if not RESULTS_FILE.exists():

        return {
            "available": False,
            "message": "No evaluation has been run yet."
        }

    with RESULTS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)
