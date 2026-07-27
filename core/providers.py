# -*- coding: utf-8 -*-
"""OpenAI + Anthropic calls, server-side (no browser CORS, no proxy needed).

Ported from the old callOpenAI/callClaude JS. Uses stdlib urllib so it runs on
Vercel serverless with zero extra dependencies and identically in the local
launcher. Returns a uniform dict: {text, cites, usage, n_search}.

The API key is passed straight through to the provider and never logged.
"""
import json
import re
import time
import urllib.error
import urllib.request

from .rules import clean_url

OPENAI_URL = "https://api.openai.com/v1/responses"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def _post(url, headers, body, timeout=300):
    """POST JSON with automatic back-off on 429 (rate limit) / 529 (overloaded)."""
    data = json.dumps(body).encode("utf-8")
    last = None
    for attempt in range(5):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            code = e.code
            text = e.read().decode("utf-8", "ignore")
            if code in (429, 529):
                ra = e.headers.get("retry-after")
                wait = int(ra) if (ra and ra.isdigit()) else min(60, 8 * (attempt + 1))
                time.sleep(wait)
                last = (code, text)
                continue
            return code, text
        except Exception as e:  # network / timeout
            msg = str(e)
            if "header value" in msg.lower():   # never echo a malformed key
                msg = "invalid request header (check the API key format)"
            last = (0, msg)
            time.sleep(min(30, 5 * (attempt + 1)))
    return last if last else (0, "request failed")


def _clean_key(key):
    # collapse any stray whitespace/newlines so a malformed key can't create an
    # invalid HTTP header (whose error text would otherwise echo the key).
    return "".join((key or "").split())


def call_openai(key, model, text_prompt, pdf_data_url=None, use_search=False, json_mode=False):
    key = _clean_key(key)
    content = [{"type": "input_text", "text": text_prompt}]
    if pdf_data_url:
        content.append({"type": "input_file", "filename": "input.pdf", "file_data": pdf_data_url})
    body = {"model": model, "input": [{"role": "user", "content": content}]}
    if use_search:
        body["tools"] = [{"type": "web_search"}]
    if json_mode:
        body["text"] = {"format": {"type": "json_object"}}
    # Reasoning models (gpt-5.x / o-series) default to HIGH effort -> with web_search they
    # run away. Force LOW effort. Do NOT send reasoning to gpt-4.1/4o (they 400).
    if re.match(r"^(gpt-5|o\d)", model, re.I):
        body["reasoning"] = {"effort": "low"}

    status, raw = _post(OPENAI_URL, {"Authorization": "Bearer " + key,
                                     "Content-Type": "application/json"}, body)
    if status != 200:
        raise RuntimeError(f"OpenAI {status}: {raw[:200]}")
    data = json.loads(raw)
    text, cites, n_search = "", [], 0
    for it in data.get("output", []):
        if "search" in (it.get("type") or ""):
            n_search += 1
        if it.get("type") == "message":
            for c in it.get("content", []):
                if c.get("type") == "output_text":
                    text += c.get("text") or ""
                    for a in c.get("annotations", []):
                        if a.get("type") == "url_citation" and a.get("url"):
                            cites.append(clean_url(a["url"]))
    u = data.get("usage", {}) or {}
    usage = {"input_tokens": u.get("input_tokens", 0), "output_tokens": u.get("output_tokens", 0)}
    return {"text": text, "cites": cites, "usage": usage, "n_search": n_search}


def call_claude(key, model, text_prompt, pdf_base64=None, use_search=False):
    key = _clean_key(key)
    content = []
    if pdf_base64:
        content.append({"type": "document",
                        "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_base64}})
    content.append({"type": "text", "text": text_prompt})
    body = {"model": model, "max_tokens": 32000, "messages": [{"role": "user", "content": content}]}
    if use_search:
        # web_search_20260209 has dynamic filtering (verified links) on Sonnet/Opus;
        # Haiku only supports the basic tool. blocked_domains enforces the exclusion.
        basic = bool(re.search(r"haiku", model, re.I))
        body["tools"] = [{
            "type": "web_search_20250305" if basic else "web_search_20260209",
            "name": "web_search",
            "max_uses": 5,
            "blocked_domains": ["degriffstock.com"],
        }]
    status, raw = _post(ANTHROPIC_URL, {"x-api-key": key,
                                        "anthropic-version": "2023-06-01",
                                        "content-type": "application/json"}, body)
    if status != 200:
        raise RuntimeError(f"Claude {status}: {raw[:200]}")
    data = json.loads(raw)
    text, cites, n_search = "", [], 0
    for block in data.get("content", []):
        bt = block.get("type")
        if bt == "text":
            text += block.get("text") or ""
            for c in (block.get("citations") or []):
                if c.get("url"):
                    cites.append(clean_url(c["url"]))
        elif bt == "web_search_tool_result":
            items = block.get("content")
            if isinstance(items, list):
                for r in items:
                    if isinstance(r, dict) and r.get("url"):
                        cites.append(clean_url(r["url"]))
        elif bt == "server_tool_use" and block.get("name") == "web_search":
            n_search += 1
    u = data.get("usage", {}) or {}
    usage = {"input_tokens": u.get("input_tokens", 0), "output_tokens": u.get("output_tokens", 0)}
    return {"text": text, "cites": cites, "usage": usage, "n_search": n_search}


def ai_call(provider, key, model, **kwargs):
    if provider == "claude":
        return call_claude(key, model,
                           text_prompt=kwargs["text_prompt"],
                           pdf_base64=kwargs.get("pdf_base64"),
                           use_search=kwargs.get("use_search", False))
    return call_openai(key, model,
                       text_prompt=kwargs["text_prompt"],
                       pdf_data_url=kwargs.get("pdf_data_url"),
                       use_search=kwargs.get("use_search", False),
                       json_mode=kwargs.get("json_mode", False))
