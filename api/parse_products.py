# -*- coding: utf-8 -*-
"""Vercel serverless: Tab 2 step 1. POST {file_base64, filename} -> {products}."""
import base64
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.excelio import read_tabular, find_products  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n) or b"{}")
            file_bytes = base64.b64decode(req.get("file_base64", ""))
            aoa = read_tabular(file_bytes, req.get("filename", ""))
            products = find_products(aoa)
            _send(self, 200, {"products": products})
        except Exception as e:
            _send(self, 200, {"error": str(e)})


def _send(self, code, obj):
    body = json.dumps(obj).encode("utf-8")
    self.send_response(code)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)
