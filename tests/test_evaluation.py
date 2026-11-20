import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services import evaluation


class EvaluateReportTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "case_id": "EVAL-001",
            "order_id": "QK-1001",
            "required_terms": " Order ; PAYMENT ; paid ;; ",
            "forbidden_terms": " Refund Completed ;; ",
        }

    def test_normalizes_terms_and_report_case(self):
        result = evaluation.evaluate_report(
            self.case, "The ORDER has a paid Payment."
        )

        self.assertEqual(result, {
            "case_id": "EVAL-001",
            "order_id": "QK-1001",
            "passed": True,
            "missing_terms": [],
            "forbidden_terms_found": [],
        })

    def test_reports_missing_and_forbidden_terms(self):
        scenarios = [
            ("Order received.", ["payment", "paid"], []),
            ("Order payment paid. REFUND COMPLETED.", [], ["refund completed"]),
            ("Order. Refund completed.", ["payment", "paid"], ["refund completed"]),
        ]

        for report, missing, forbidden in scenarios:
            with self.subTest(report=report):
                result = evaluation.evaluate_report(self.case, report)

                self.assertFalse(result["passed"])
                self.assertEqual(result["missing_terms"], missing)
                self.assertEqual(result["forbidden_terms_found"], forbidden)

    def test_ignores_empty_term_entries(self):
        self.case["required_terms"] = " ; ; "
        self.case["forbidden_terms"] = ""

        result = evaluation.evaluate_report(self.case, "")

        self.assertTrue(result["passed"])
        self.assertEqual(result["missing_terms"], [])
        self.assertEqual(result["forbidden_terms_found"], [])


class EvaluateAllTests(unittest.TestCase):
    def test_aggregates_pass_failure_and_missing_report(self):
        cases = [
            {
                "case_id": f"EVAL-00{index}",
                "order_id": f"QK-100{index}",
                "required_terms": "order;paid",
                "forbidden_terms": "refund completed",
            }
            for index in range(1, 4)
        ]
        reports = {
            "QK-1001": "Order paid.",
            "QK-1002": "Order pending.",
            "QK-9999": "Order paid.",
        }

        with patch.object(evaluation, "load_cases", return_value=cases):
            result = evaluation.evaluate_all(reports)

        self.assertEqual(result, {
            "evaluation_type": "keyword_and_policy_check",
            "total": 3,
            "passed": 1,
            "failed": 2,
            "pass_rate": 33.33,
            "results": [
                {
                    "case_id": "EVAL-001",
                    "order_id": "QK-1001",
                    "passed": True,
                    "missing_terms": [],
                    "forbidden_terms_found": [],
                },
                {
                    "case_id": "EVAL-002",
                    "order_id": "QK-1002",
                    "passed": False,
                    "missing_terms": ["paid"],
                    "forbidden_terms_found": [],
                },
                {
                    "case_id": "EVAL-003",
                    "order_id": "QK-1003",
                    "passed": False,
                    "missing_terms": [],
                    "forbidden_terms_found": [],
                    "error": "No actual investigation report supplied.",
                },
            ],
        })

    def test_handles_no_cases(self):
        with patch.object(evaluation, "load_cases", return_value=[]):
            result = evaluation.evaluate_all({})

        self.assertEqual(result["total"], 0)
        self.assertEqual(result["passed"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["pass_rate"], 0)
        self.assertEqual(result["results"], [])


class EvaluationFileTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.directory = Path(temporary_directory.name) / "evaluations"
        self.cases_file = self.directory / "cases.csv"
        self.results_file = self.directory / "latest.json"

        for name, value in (
            ("EVALUATION_DIR", self.directory),
            ("CASES_FILE", self.cases_file),
            ("RESULTS_FILE", self.results_file),
        ):
            patcher = patch.object(evaluation, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_loads_csv_cases(self):
        cases = [
            {
                "case_id": "EVAL-001",
                "order_id": "QK-1001",
                "required_terms": "order;payment, paid",
                "forbidden_terms": "refund completed",
            },
            {
                "case_id": "EVAL-002",
                "order_id": "QK-1002",
                "required_terms": "order;pending",
                "forbidden_terms": "",
            },
        ]
        self.directory.mkdir()
        with self.cases_file.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(cases[0]))
            writer.writeheader()
            writer.writerows(cases)

        self.assertEqual(evaluation.load_cases(), cases)

    def test_missing_cases_raise_with_file_path(self):
        with self.assertRaises(FileNotFoundError) as error:
            evaluation.load_cases()

        self.assertIn(str(self.cases_file), str(error.exception))

    def test_save_creates_directory_and_round_trips_results(self):
        result = {
            "evaluation_type": "keyword_and_policy_check",
            "total": 1,
            "passed": 1,
            "failed": 0,
            "pass_rate": 100.0,
            "results": [{"case_id": "EVAL-001", "passed": True}],
        }

        evaluation.save_results(result)

        with self.results_file.open(encoding="utf-8") as file:
            self.assertEqual(json.load(file), result)
        self.assertEqual(evaluation.load_latest_results(), result)

    def test_missing_latest_results_are_unavailable(self):
        self.assertEqual(evaluation.load_latest_results(), {
            "available": False,
            "message": "No evaluation has been run yet.",
        })

    def test_invalid_latest_json_raises(self):
        self.directory.mkdir()
        self.results_file.write_text("{invalid json", encoding="utf-8")

        with self.assertRaises(json.JSONDecodeError):
            evaluation.load_latest_results()


if __name__ == "__main__":
    unittest.main()
