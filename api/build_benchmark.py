# -*- coding: utf-8 -*-
"""Vercel serverless: Tab 2 download. POST {rows} -> {xlsx_base64}."""
import base64
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.excelio import build_dispatch_benchmark  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n) or b"{}")
            built = build_dispatch_benchmark(req.get("rows", []))
            _send(self, 200, {"xlsx_base64": base64.b64encode(built["xlsx"]).decode("ascii")})
        except Exception as e:
            _send(self, 200, {"error": str(e)})


def _send(self, code, obj):
    body = json.dumps(obj).encode("utf-8")
    self.send_response(code)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)
