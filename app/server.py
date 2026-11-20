
import json
import time

from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer
)

from pathlib import Path
from uuid import UUID, uuid4

from app.config import (
    APP_HOST,
    APP_PORT,
    DATA_DIR,
    AUDIT_DIR
)

from app.business import get_order

from app.agents.orchestrator import investigate_sync

from app.services.approval import (
    load_approvals,
    request_approval,
    decide_approval
)

from app.services.audit import write_audit

from app.services.guardrails import (
    validate_order_id,
    check_action
)

from app.services.telemetry import record_http

from app.services.observability import get_metrics

from app.services.evaluation import load_latest_results


ROOT = Path(__file__).resolve().parents[1]

APP_DIR = ROOT / "app"

INVESTIGATIONS_DIR = DATA_DIR / "investigations"

GOVERNANCE_FILE = DATA_DIR / "governance_controls.json"

INVESTIGATIONS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


PAGE_FILES = {

    "/": "dashboard.html",

    "/dashboard": "dashboard.html",

    "/app": "workspace.html",

    "/review": "review.html",

    "/operations": "operations.html"
}


def read_json(filename):

    path = DATA_DIR / filename

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_investigation(investigation_id):

    if not investigation_id:

        raise ValueError(
            "Investigation reference is required."
        )

    try:

        safe_id = str(
            UUID(str(investigation_id))
        )

    except (ValueError, TypeError, AttributeError):

        raise ValueError(
            "Invalid investigation reference."
        )

    path = (
        INVESTIGATIONS_DIR
        / f"{safe_id}.json"
    )

    if not path.exists():

        raise ValueError(
            "Investigation was not found."
        )

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


class QuickKartHandler(BaseHTTPRequestHandler):

    def send_response_data(
        self,
        status,
        content,
        content_type="application/json; charset=utf-8"
    ):

        body = content.encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            content_type
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(body)

    def send_json(self, status, payload):

        return self.send_response_data(
            status,
            json.dumps(
                payload,
                default=str
            ),
            "application/json; charset=utf-8"
        )

    def send_page(self, filename):

        path = APP_DIR / filename

        if not path.exists():

            return self.send_json(
                404,
                {
                    "error": f"Page {filename} not found."
                }
            )

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            html = file.read()

        return self.send_response_data(
            200,
            html,
            "text/html; charset=utf-8"
        )

    def read_payload(self):

        length = int(
            self.headers.get(
                "Content-Length",
                "0"
            )
        )

        if length < 1:

            raise ValueError(
                "Request body is required."
            )

        if length > 20000:

            raise ValueError(
                "Request body is too large."
            )

        raw = self.rfile.read(length)

        return json.loads(
            raw.decode("utf-8")
        )

    def do_GET(self):

        started = time.perf_counter()

        status_code = 200

        try:

            path = self.path.split(
                "?",
                1
            )[0]

            # Application pages

            if path in PAGE_FILES:

                return self.send_page(
                    PAGE_FILES[path]
                )

            # Original Day 1 strategy API

            if path == "/api/strategy":

                response = {

                    "business": read_json(
                        "business_case.json"
                    ),

                    "frameworks": read_json(
                        "framework_options.json"
                    ),

                    "architecture": read_json(
                        "architecture.json"
                    ),

                    "responsible_ai": read_json(
                        "responsible_ai.json"
                    ),

                    "roi": read_json(
                        "roi_assumptions.json"
                    )
                }

                return self.send_json(
                    200,
                    response
                )

            # Approval queue

            if path == "/api/approvals":

                return self.send_json(
                    200,
                    {
                        "approvals": load_approvals()
                    }
                )

            # Monitoring metrics

            if path == "/api/metrics":

                return self.send_json(
                    200,
                    get_metrics()
                )

            # Evaluation results

            if path == "/api/evaluations":

                return self.send_json(
                    200,
                    load_latest_results()
                )

            # Governance controls

            if path == "/api/governance":

                return self.send_json(
                    200,
                    read_json(
                        "governance_controls.json"
                    )
                )

            # Saved investigations

            if path == "/api/investigations":

                records = []

                for file in sorted(
                    INVESTIGATIONS_DIR.glob("*.json"),
                    reverse=True
                ):

                    try:

                        with file.open(
                            "r",
                            encoding="utf-8"
                        ) as data_file:

                            records.append(
                                json.load(data_file)
                            )

                    except (
                        json.JSONDecodeError,
                        OSError
                    ):

                        continue

                return self.send_json(
                    200,
                    {
                        "investigations": records[:30]
                    }
                )

            # Audit history

            if path == "/api/audit":

                audit_file = (
                    AUDIT_DIR / "events.jsonl"
                )

                events = []

                if audit_file.exists():

                    with audit_file.open(
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

                return self.send_json(
                    200,
                    {
                        "events": events[-100:]
                    }
                )

            status_code = 404

            return self.send_json(
                status_code,
                {
                    "error": "Endpoint not found."
                }
            )

        except Exception as error:

            status_code = 500

            return self.send_json(
                status_code,
                {
                    "error": str(error)
                }
            )

        finally:

            record_http(
                "GET",
                self.path,
                status_code,
                (
                    time.perf_counter() - started
                ) * 1000
            )

    def do_POST(self):

        started = time.perf_counter()

        status_code = 200

        try:

            payload = self.read_payload()

            path = self.path.split(
                "?",
                1
            )[0]

            # Original Day 1 architecture decision

            if path == "/api/decision":

                allowed = {

                    "copilot_studio",

                    "agent_framework",

                    "foundry",

                    "dynamics",

                    "m365"
                }

                choice = payload.get(
                    "choice",
                    ""
                )

                rationale = str(
                    payload.get(
                        "rationale",
                        ""
                    )
                ).strip()

                if choice not in allowed:

                    raise ValueError(
                        "Invalid framework selection."
                    )

                if not rationale:

                    raise ValueError(
                        "Architecture rationale is required."
                    )

                decision = {

                    "selected_framework": choice,

                    "rationale": rationale
                }

                output = DATA_DIR / "decisions.json"

                with output.open(
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(
                        decision,
                        file,
                        indent=2
                    )

                write_audit(
                    "framework_decision_saved",
                    "WorkshopUser",
                    decision
                )

                return self.send_json(
                    200,
                    {
                        "success": True,
                        "decision": decision
                    }
                )

            # Run the six-agent investigation

            if path == "/api/investigate":

                order_id = str(
                    payload.get(
                        "order_id",
                        ""
                    )
                ).strip()

                validate_order_id(
                    order_id
                )

                order = get_order(
                    order_id
                )

                if order is None:

                    raise ValueError(
                        f"Order {order_id} was not found."
                    )

                result = investigate_sync(
                    order_id
                )

                investigation_id = str(
                    uuid4()
                )

                record = {

                    "investigation_id": investigation_id,

                    "order_id": order_id,

                    "created_at": time.strftime(
                        "%Y-%m-%dT%H:%M:%SZ",
                        time.gmtime()
                    ),

                    "agents": result["agents"],

                    "final_report": result["final_report"]
                }

                output = (
                    INVESTIGATIONS_DIR
                    / f"{investigation_id}.json"
                )

                with output.open(
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(
                        record,
                        file,
                        indent=2
                    )

                write_audit(
                    "investigation_completed",
                    "QuickKartAgent",
                    {
                        "investigation_id": investigation_id,
                        "order_id": order_id
                    }
                )

                return self.send_json(
                    200,
                    record
                )

            # Create a human approval request

            if path == "/api/approvals/request":

                investigation_id = payload.get(
                    "investigation_id"
                )

                investigation = load_investigation(
                    investigation_id
                )

                action = str(
                    payload.get(
                        "action",
                        ""
                    )
                ).strip()

                reason = str(
                    payload.get(
                        "reason",
                        ""
                    )
                ).strip()

                allowed_actions = {

                    "execute_refund",

                    "cancel_order",

                    "manual_review"
                }

                if action not in allowed_actions:

                    raise ValueError(
                        "Action is not in the approval allowlist."
                    )

                if not reason:

                    raise ValueError(
                        "Approval reason is required."
                    )

                guardrail = check_action(
                    action
                )

                if not guardrail.get(
                    "requires_approval"
                ):

                    raise ValueError(
                        "The action does not require approval."
                    )

                approval = request_approval(
                    order_id=investigation["order_id"],
                    action=action,
                    reason=reason,
                    investigation_id=investigation_id
                )

                return self.send_json(
                    201,
                    {
                        "approval": approval
                    }
                )

            # Human approval or rejection

            if path == "/api/approvals/decision":

                approval_id = str(
                    payload.get(
                        "approval_id",
                        ""
                    )
                ).strip()

                decision = str(
                    payload.get(
                        "decision",
                        ""
                    )
                ).strip()

                approver = str(
                    payload.get(
                        "approver",
                        ""
                    )
                ).strip()

                comment = str(
                    payload.get(
                        "comment",
                        ""
                    )
                ).strip()

                if not comment:

                    raise ValueError(
                        "Reviewer comment is required."
                    )

                approval = decide_approval(
                    approval_id=approval_id,
                    decision=decision,
                    approver=approver,
                    comment=comment
                )

                return self.send_json(
                    200,
                    {
                        "approval": approval
                    }
                )

            status_code = 404

            return self.send_json(
                status_code,
                {
                    "error": "Endpoint not found."
                }
            )

        except (
            ValueError,
            json.JSONDecodeError
        ) as error:

            status_code = 400

            return self.send_json(
                status_code,
                {
                    "error": str(error)
                }
            )

        except Exception as error:

            status_code = 500

            return self.send_json(
                status_code,
                {
                    "error": str(error)
                }
            )

        finally:

            record_http(
                "POST",
                self.path,
                status_code,
                (
                    time.perf_counter() - started
                ) * 1000
            )

    def log_message(self, format, *args):

        print(
            format % args
        )


if __name__ == "__main__":

    server = ThreadingHTTPServer(
        (APP_HOST, APP_PORT),
        QuickKartHandler
    )

    print()
    print("=" * 55)
    print("QUICKKART OPERATIONS WORKSPACE")
    print("=" * 55)
    print()
    print(
        f"Application: http://{APP_HOST}:{APP_PORT}/app"
    )
    print(
        f"Strategy:    http://{APP_HOST}:{APP_PORT}/dashboard"
    )
    print(
        f"Review:      http://{APP_HOST}:{APP_PORT}/review"
    )
    print(
        f"Monitoring:  http://{APP_HOST}:{APP_PORT}/operations"
    )
    print()

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "Stopping QuickKart server."
        )

    finally:

        server.server_close()
