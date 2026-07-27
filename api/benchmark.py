# -*- coding: utf-8 -*-
"""Vercel serverless: Tab 2 loop. POST {product, provider, model, key, is_demo} -> one row."""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.benchmark import benchmark_product  # noqa: E402
from core.rules import to_rayon               # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n) or b"{}")
            p = req.get("product", {})
            if req.get("is_demo"):
                row = {"no": p.get("no"), "rayon": to_rayon(p.get("rayon")), "model": p.get("model"),
                       "ean": p.get("ean"), "designation": p.get("designation"), "qty": p.get("qty"),
                       "paht": p.get("paht"), "price_avg": 25, "price_high": 30, "price_low": 20,
                       "benchmarking_reference": "brandalley.fr ; veepee.fr"}
                _send(self, 200, {"row": row, "usage": {}, "n_search": 0, "n_live": 2})
                return
            res = benchmark_product(p, provider=req.get("provider", "openai"),
                                    key=req.get("key", ""), model=req.get("model", ""))
            _send(self, 200, res)
        except Exception as e:
            _send(self, 200, {"error": str(e)})


def _send(self, code, obj):
    body = json.dumps(obj).encode("utf-8")
    self.send_response(code)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)
