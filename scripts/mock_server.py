"""Локальный mock-стенд, повторяющий контракт демо-API https://reqres.in.

Позволяет гонять API-тесты без лимита публичного стенда (40 запросов/день с IP).
Работает только на стандартной библиотеке Python — зависимости не нужны.

Поднять стенд:
    python scripts/mock_server.py            # порт 8765 по умолчанию
    python scripts/mock_server.py --port 9000

Прогнать тесты на этом стенде:
    BASE_URL=http://127.0.0.1:8765/api pytest
"""
import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

EXISTING_USER_IDS = range(1, 13)  # как в reqres.in: существуют пользователи 1..12


class MockHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body=None):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if body is not None:
            self.wfile.write(json.dumps(body).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_POST(self):
        body = self._read_body()
        if self.path in ("/api/register", "/api/login"):
            if body.get("email") and body.get("password"):
                self._send(200, {"token": "mock-token"})
            else:
                self._send(400, {"error": "Missing email or username"})
        elif self.path == "/api/users":
            self._send(201, {"id": "999", **body})
        else:
            self._send(404, {})

    def do_GET(self):
        parsed = urlparse(self.path)
        match = re.fullmatch(r"/api/users/(\d+)", parsed.path)
        if match:
            user_id = int(match.group(1))
            if user_id in EXISTING_USER_IDS:
                self._send(200, {"data": {"id": user_id}})
            else:
                self._send(404, {})
        elif parsed.path == "/api/users":
            page = int(parse_qs(parsed.query).get("page", ["1"])[0])
            self._send(200, {"page": page, "data": [{"id": 7}, {"id": 8}, {"id": 9}]})
        else:
            self._send(404, {})

    def do_PUT(self):
        body = self._read_body()
        if re.fullmatch(r"/api/users/(\d+)", urlparse(self.path).path):
            self._send(200, body)
        else:
            self._send(404, {})

    def do_DELETE(self):
        if re.fullmatch(r"/api/users/(\d+)", urlparse(self.path).path):
            self._send(204)
        else:
            self._send(404, {})


def main():
    parser = argparse.ArgumentParser(description="Локальный mock-стенд API")
    parser.add_argument("--port", type=int, default=8765, help="порт (по умолчанию 8765)")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), MockHandler)
    print(f"Mock-стенд поднят: http://127.0.0.1:{args.port}/api")
    server.serve_forever()


if __name__ == "__main__":
    main()
