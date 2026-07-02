"""Vercel serverless function: server-side link check to drop dead URLs.
Catches hard 404/410 AND "soft 404s" (HTTP 200 but the page content is a not-found page)."""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import re
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "Chrome/124 Safari/537.36")
SOFT = re.compile(r"404|not\s*found|page\s*introuvable|introuvable|non\s*trouv|page not found", re.I)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        target = (parse_qs(urlparse(self.path).query).get("url") or [""])[0]
        status, dead = 0, False
        try:
            req = urllib.request.Request(target, method="GET",
                                         headers={"User-Agent": UA, "Accept": "text/html,*/*"})
            with urllib.request.urlopen(req, timeout=9) as up:
                status = up.status
                final = up.geturl()
                ctype = up.headers.get_content_type()
                body = up.read(80000).decode("utf-8", "ignore") if ("html" in ctype or "text" in ctype) else ""
            m = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
            title = m.group(1).strip() if m else ""
            if status in (404, 410):
                dead = True
            elif SOFT.search(title) or "/404" in (final or ""):
                dead = True
        except urllib.error.HTTPError as e:
            status = e.code; dead = e.code in (404, 410)
        except Exception:
            status = 0  # unverifiable — caller keeps it
        out = json.dumps({"url": target, "status": status, "dead": dead}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)
