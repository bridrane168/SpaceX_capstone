"""Run the Dash app when installed; otherwise serve the self-contained HTML dashboard."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
import pandas as pd
import webbrowser

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = Path(__file__).resolve().parent
PAGE = (DASHBOARD_DIR / "index.html").read_bytes()
DATA = pd.read_csv(ROOT / "spacex_cleaned_data.csv")
required = {"Class", "LaunchSite", "Orbit"}
missing = required - set(DATA.columns)
if missing:
    raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
DATA["Class"] = pd.to_numeric(DATA["Class"], errors="coerce")
if "PayloadMass" in DATA:
    DATA["PayloadMass"] = pd.to_numeric(DATA["PayloadMass"], errors="coerce")
records = json.dumps(DATA.where(pd.notna(DATA), None).to_dict(orient="records"), ensure_ascii=False).replace("</", "<\\/").encode("utf-8")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            body, content_type = PAGE, "text/html; charset=utf-8"
        elif self.path == "/data":
            body, content_type = records, "application/json; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, fmt, *args):
        print("[dashboard] " + fmt % args)

if __name__ == "__main__":
    try:
        from dash_app import app
    except ImportError:
        print("Dash is not installed; serving the interactive standalone dashboard.")
        print("Dashboard available at http://127.0.0.1:8050")
        try:
            server = HTTPServer(("127.0.0.1", 8050), Handler)
        except OSError as exc:
            page = (DASHBOARD_DIR / "index.html").resolve()
            print(f"Could not bind the local server ({exc}); opening {page} directly.")
            webbrowser.open(page.as_uri())
        else:
            webbrowser.open("http://127.0.0.1:8050/")
            server.serve_forever()
    else:
        print("Dash dashboard available at http://127.0.0.1:8050")
        webbrowser.open("http://127.0.0.1:8050/")
        app.run(debug=False, host="127.0.0.1", port=8050)
