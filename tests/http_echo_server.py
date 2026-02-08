#!/usr/bin/env python3
"""Simple HTTP server that captures requests and returns payload as JSON.

Used by tests to validate send.py: POST requests are captured and answered
with a Mailjet-like success response; GET /last-request returns the last
captured request as JSON for assertions.
"""
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Optional


# Last captured request: {method, path, headers, body}
_last_request: Optional[dict[str, Any]] = None

# Mailjet success response so send.py does not fail
SUCCESS_RESPONSE = b'{"Messages": [{"Status": "success"}]}'


class CaptureHandler(BaseHTTPRequestHandler):
    """Handler that captures request and returns success or last request."""

    def _capture(self, body_json: Any) -> None:
        global _last_request
        headers = {k: v for k, v in self.headers.items()}
        _last_request = {
            "method": self.command,
            "path": self.path,
            "headers": headers,
            "body": body_json,
        }

    def _send_json(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length) if content_length else b""
        try:
            body = json.loads(raw.decode("utf-8")) if raw else None
        except (ValueError, UnicodeDecodeError):
            body = raw.decode("utf-8", errors="replace")
        self._capture(body)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(SUCCESS_RESPONSE)))
        self.end_headers()
        self.wfile.write(SUCCESS_RESPONSE)

    def do_GET(self) -> None:
        global _last_request

        if self.path == "/last-request":
            if _last_request is None:
                self._send_json({"error": "no request captured yet"}, 404)
            else:
                self._send_json(_last_request)
            return
        
        self._send_json({"error": "use GET /last-request to see captured request"}, 404)

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default request logging during tests."""
        pass


def get_captured_request() -> Optional[dict[str, Any]]:
    """Return the last captured request (for tests)."""
    return _last_request


def clear_captured_request() -> None:
    """Clear the last captured request (for tests)."""
    global _last_request
    _last_request = None



def run_server(port: int) -> tuple[HTTPServer, int]:
    """Start the capture server in a thread. Returns (server, port). """
    server = HTTPServer(("127.0.0.1", port), CaptureHandler)
    actual_port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, actual_port

if __name__ == "__main__":
    port = 8080
    server = HTTPServer(("127.0.0.1", port), CaptureHandler)
    print(f"Echo server at http://127.0.0.1:{port} (GET /last-request for last request)")
    server.serve_forever()
