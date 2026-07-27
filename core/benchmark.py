# -*- coding: utf-8 -*-
"""Per-product price benchmarking + server-side link validation (soft-404 aware).
One product per call so each fits inside a serverless invocation.
"""
import re
import urllib.error
import urllib.request

from .extract import parse_json
from .prompts import build_bench_prompt
from .providers import ai_call
from .rules import to_rayon

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36")
_SOFT = re.compile(r"404|not\s*found|page\s*introuvable|introuvable|non\s*trouv|page not found", re.I)


def check_url(url):
    """Return (status, dead). Catches hard 404/410 AND soft-404 (200 but a not-found page)."""
    try:
        req = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": _UA, "Accept": "text/html,*/*"})
        with urllib.request.urlopen(req, timeout=9) as up:
            status = up.status
            final = up.geturl()
            ctype = up.headers.get_content_type()
            body = up.read(80000).decode("utf-8", "ignore") if ("html" in ctype or "text" in ctype) else ""
        m = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
        title = m.group(1).strip() if m else ""
        dead = status in (404, 410) or bool(_SOFT.search(title)) or "/404" in (final or "")
        return status, dead
    except urllib.error.HTTPError as e:
        return e.code, e.code in (404, 410)
    except Exception:
        return 0, False   # transient/unverifiable -> keep


def validate_urls(urls):
    """Drop dead links (404/410/soft-404); keep everything else."""
    keep = []
    for u in urls:
        _, dead = check_url(u)
        if not dead:
            keep.append(u)
    return keep


def benchmark_product(p, *, provider, key, model):
    """p: dict from find_products (brand/designation/ean/color/size/qty/paht/rayon/model).
    Returns a benchmark row dict ready for build_dispatch_benchmark."""
    out = ai_call(provider, key, model, text_prompt=build_bench_prompt(p), use_search=True)
    j = parse_json(out["text"]) or {}
    clean = [u for u in dict.fromkeys(out["cites"]) if not re.search(r"degriffstock", u, re.I)]
    live = validate_urls(clean[:8])
    refs = " ; ".join(live[:5]) or "No live link found"
    return {
        "row": {
            "no": p.get("no"), "rayon": to_rayon(p.get("rayon")), "model": p.get("model"),
            "ean": p.get("ean"), "designation": p.get("designation"), "qty": p.get("qty"),
            "paht": p.get("paht"), "price_avg": j.get("price_avg"), "price_high": j.get("price_high"),
            "price_low": j.get("price_low"), "benchmarking_reference": refs,
        },
        "usage": out["usage"], "n_search": out["n_search"], "n_live": len(live),
    }
