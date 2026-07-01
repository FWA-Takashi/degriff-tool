"""Vercel serverless function: proxy browser -> Anthropic (Claude).
The user's API key arrives in x-api-key and is only forwarded, never stored. Stdlib only."""
from http.server import BaseHTTPRequestHandler
import json
import urllib.error
import urllib.request

UPSTREAM = "https://api.anthropic.com/v1/messages"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", 0))
        body = self.rfile.read(length) if length else b""
        headers = {"Content-Type": "application/json"}
        for h in ("x-api-key", "anthropic-version"):
            v = self.headers.get(h)
            if v:
                headers[h] = v
        headers.setdefault("anthropic-version", "2023-06-01")
        req = urllib.request.Request(UPSTREAM, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=58) as up:
                data, status = up.read(), up.status
        except urllib.error.HTTPError as e:
            data, status = e.read(), e.code
        except Exception as e:
            data, status = json.dumps({"error": {"message": f"Proxy error: {e}"}}).encode(), 502
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)
