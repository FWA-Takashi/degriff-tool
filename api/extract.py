# -*- coding: utf-8 -*-
"""Vercel serverless: Tab 1 extraction. POST JSON -> rows + warnings + debug + built files."""
import base64
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.extract import extract          # noqa: E402
from core.excelio import build_creation_dispatch  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n) or b"{}")
            file_bytes = base64.b64decode(req.get("file_base64", "")) if req.get("file_base64") else b""
            res = extract(
                file_bytes, req.get("filename", ""),
                provider=req.get("provider", "openai"), key=req.get("key", ""),
                model=req.get("model", ""), lang=req.get("lang", "en"),
                include_enrich=bool(req.get("include_enrich")),
                include_barcode=bool(req.get("include_barcode")),
                web_enrich=bool(req.get("web_enrich")),
                supplier_override=req.get("supplier_override", ""),
                is_demo=bool(req.get("is_demo")),
            )
            built = build_creation_dispatch(res["rows"], bool(req.get("include_enrich")),
                                            bool(req.get("include_barcode")))
            res["files"] = {
                "xlsx_base64": base64.b64encode(built["xlsx"]).decode("ascii"),
                "creation_csv": built["creation_csv"],
                "dispatch_csv": built["dispatch_csv"],
            }
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
