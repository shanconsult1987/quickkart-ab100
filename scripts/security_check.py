
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.guardrails import check_action


ROOT = Path(__file__).resolve().parents[1]

GOVERNANCE_FILE = (
    ROOT / "data" / "governance_controls.json"
)

GITIGNORE_FILE = ROOT / ".gitignore"


REQUIRED_CONTROLS = {
    "GOV-001",
    "GOV-002",
    "GOV-003",
    "GOV-004",
    "GOV-005",
    "GOV-006",
    "GOV-007",
}


REQUIRED_IGNORE_ENTRIES = [
    ".env",
    ".venv/",
    "__pycache__/",
]


BLOCKED_BUSINESS_ACTIONS = [
    "execute_refund",
    "issue_refund",
    "cancel_order",
    "update_payment",
    "modify_inventory",
    "delete_order",
]


def validate_governance_file():

    if not GOVERNANCE_FILE.exists():

        raise FileNotFoundError(
            "Governance controls file is missing."
        )

    with GOVERNANCE_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        configuration = json.load(file)

    controls = configuration.get("controls", [])

    control_ids = {
        control.get("id")
        for control in controls
    }

    missing = REQUIRED_CONTROLS - control_ids

    if missing:

        raise ValueError(
            f"Missing governance controls: {sorted(missing)}"
        )

    disabled = [
        control.get("id")
        for control in controls
        if control.get("enabled") is not True
    ]

    if disabled:

        raise ValueError(
            f"Disabled governance controls: {disabled}"
        )

    print("[PASS] Governance controls are present and enabled.")


def validate_gitignore():

    if not GITIGNORE_FILE.exists():

        raise FileNotFoundError(
            ".gitignore file is missing."
        )

    content = GITIGNORE_FILE.read_text(
        encoding="utf-8"
    )

    lines = {
        line.strip()
        for line in content.splitlines()
    }

    missing = [
        entry
        for entry in REQUIRED_IGNORE_ENTRIES
        if entry not in lines and entry.rstrip("/") not in lines
    ]

    if missing:

        raise ValueError(
            f"Missing .gitignore entries: {missing}"
        )

    print("[PASS] Required local files are excluded from Git.")


def validate_guardrails():

    failures = []

    for action in BLOCKED_BUSINESS_ACTIONS:

        result = check_action(action)

        if result.get("allowed") is not False:

            failures.append(
                f"{action} should not be allowed directly."
            )

        if result.get("requires_approval") is not True:

            failures.append(
                f"{action} must require human approval."
            )

    if failures:

        raise ValueError(
            "\n".join(failures)
        )

    print("[PASS] Financial and mutation actions require approval.")


def main():

    print()
    print("=" * 55)
    print("QUICKKART GOVERNANCE AND SECURITY VALIDATION")
    print("=" * 55)

    checks = [
        validate_governance_file,
        validate_gitignore,
        validate_guardrails,
    ]

    errors = []

    for check in checks:

        try:

            check()

        except Exception as error:

            errors.append(str(error))

            print(f"[FAIL] {error}")

    print()

    if errors:

        print("GOVERNANCE VALIDATION FAILED")

        raise SystemExit(1)

    print("ALL GOVERNANCE CHECKS PASSED")


if __name__ == "__main__":

    main()
