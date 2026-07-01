"""Vercel serverless function: proxy browser -> OpenAI (OpenAI blocks direct browser CORS).
The user's API key arrives in the Authorization header and is only forwarded, never stored.
Stdlib only -> no requirements.txt needed."""
from http.server import BaseHTTPRequestHandler
import json
import urllib.error
import urllib.request

UPSTREAM = "https://api.openai.com/v1/responses"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", 0))
        body = self.rfile.read(length) if length else b""
        headers = {"Content-Type": "application/json"}
        auth = self.headers.get("Authorization")
        if auth:
            headers["Authorization"] = auth
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
