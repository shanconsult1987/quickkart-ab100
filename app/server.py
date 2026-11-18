import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DASHBOARD = ROOT / "app" / "dashboard.html"

def read_json(filename):
    path = DATA / filename

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

class DashboardHandler(BaseHTTPRequestHandler):

    def send_response_data(self, status, content, content_type):
        body = content.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        if self.path in ["/", "/dashboard"]:

            with DASHBOARD.open("r", encoding="utf-8") as file:
                html = file.read()

            return self.send_response_data(
                200,
                html,
                "text/html; charset=utf-8"
            )

        if self.path == "/api/strategy":

            response = {
                "business": read_json("business_case.json"),
                "frameworks": read_json("framework_options.json"),
                "architecture": read_json("architecture.json"),
                "responsible_ai": read_json("responsible_ai.json"),
                "roi": read_json("roi_assumptions.json")
            }

            return self.send_response_data(
                200,
                json.dumps(response),
                "application/json"
            )

        return self.send_response_data(
            404,
            json.dumps({"error": "Not found"}),
            "application/json"
        )

    def do_POST(self):

        if self.path != "/api/decision":

            return self.send_response_data(
                404,
                json.dumps({"error": "Unknown endpoint"}),
                "application/json"
            )

        try:

            length = int(self.headers.get("Content-Length", 0))

            if length > 10000:
                raise ValueError("Request too large")

            payload = json.loads(
                self.rfile.read(length).decode("utf-8")
            )

            allowed = {
                "copilot_studio",
                "agent_framework",
                "foundry",
                "dynamics",
                "m365"
            }

            choice = payload.get("choice", "")
            rationale = str(payload.get("rationale", "")).strip()

            if choice not in allowed:
                raise ValueError("Invalid framework selection")

            if not rationale:
                raise ValueError("Please provide an architecture rationale")

            decision = {
                "selected_framework": choice,
                "rationale": rationale
            }

            output = DATA / "decisions.json"

            output.write_text(
                json.dumps(decision, indent=2),
                encoding="utf-8"
            )

            return self.send_response_data(
                200,
                json.dumps({
                    "success": True,
                    "decision": decision
                }),
                "application/json"
            )

        except (ValueError, json.JSONDecodeError) as error:

            return self.send_response_data(
                400,
                json.dumps({"error": str(error)}),
                "application/json"
            )

    def log_message(self, format, *args):
        print(format % args)


if __name__ == "__main__":

    server = ThreadingHTTPServer(
        ("127.0.0.1", 8080),
        DashboardHandler
    )

    print("QuickKart Executive Decision Dashboard")
    print("Open http://127.0.0.1:8080")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("Stopping dashboard")

    finally:
        server.server_close()