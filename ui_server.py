from __future__ import annotations

import http.server
import json
import socketserver
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline import run_pipeline, get_pipeline_steps

PORT = 8000
ROOT_DIR = Path(__file__).resolve().parent
SOURCES_DIR = ROOT_DIR / "data" / "sources"


class CandidateUIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        # Route root path to index.html
        if self.path in ("/", "/index.html"):
            index_path = ROOT_DIR / "ui" / "index.html"
            if index_path.exists():
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(index_path.read_bytes())
                return
            else:
                self.send_error(404, "index.html not found in ui directory")
                return

        # Otherwise delegate to standard file server
        super().do_GET()

    def do_POST(self) -> None:
        if self.path in ("/api/candidates", "/api/pipeline-steps"):
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

            config = None
            if post_data:
                try:
                    config = json.loads(post_data.decode("utf-8"))
                except Exception as exc:
                    self.send_error(400, f"Invalid JSON config: {exc}")
                    return

            try:
                if self.path == "/api/pipeline-steps":
                    results = get_pipeline_steps(SOURCES_DIR, config)
                else:
                    results = run_pipeline(SOURCES_DIR, config)
                    
                response_bytes = json.dumps(results, ensure_ascii=False).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(response_bytes)))
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as exc:
                self.send_error(500, f"Pipeline run failed: {exc}")
            return

        self.send_error(404, "Endpoint not found")


def main() -> None:
    # Use socketserver to avoid port bind issues and allow fast reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CandidateUIHandler) as httpd:
        print(f"=== Eightfold Candidate Data Transformer UI Server ===")
        print(f"  UI URL: http://localhost:{PORT}")
        print(f"  Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            httpd.server_close()
            sys.exit(0)


if __name__ == "__main__":
    main()
