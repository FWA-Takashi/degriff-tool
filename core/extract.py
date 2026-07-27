# -*- coding: utf-8 -*-
"""Extraction pipeline: build prompt -> call AI -> parse/repair JSON -> validate.
Returns rows plus a debug payload so accuracy problems are inspectable.
"""
import base64
import json
import re

from . import demo
from .prompts import build_extract_prompt
from .providers import ai_call
from .validate import validate_rows


def parse_json(text):
    """Faithful port of the old parseJSON(): tolerant JSON extraction with salvage,
    so one malformed object can't lose the whole response."""
    if not text:
        return None
    t = re.sub(r"```json", "", text, flags=re.I).replace("```", "")
    m = re.search(r"\{.*\}", t, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    # Fallback: salvage individual {...} objects
    objs = re.findall(r"\{[^{}]*\}", t)
    parsed = []
    for o in objs:
        try:
            parsed.append(json.loads(o))
        except Exception:
            pass
    if not parsed:
        return None
    row_like = [r for r in parsed if isinstance(r, dict) and ("designation" in r or "size" in r)]
    return {"rows": row_like} if len(row_like) > 1 else parsed[0]


def extract(file_bytes, filename, *, provider, key, model, lang="en",
            include_enrich=False, include_barcode=False, web_enrich=False,
            supplier_override="", is_demo=False):
    """Run one extraction. Returns:
    {rows, warnings, debug:{raw, usage, n_search, source, prompt_chars}}"""
    ext = (filename or "").rsplit(".", 1)[-1].lower()

    if is_demo:
        rows = demo.extract_rows()
        if not include_enrich:
            for r in rows:
                r.pop("enriched_data", None)
        _apply_supplier(rows, supplier_override)
        return {"rows": rows, "warnings": validate_rows(rows, None),
                "debug": {"raw": "(DEMO)", "usage": {}, "n_search": 0, "source": "demo", "prompt_chars": 0}}

    text_prompt = build_extract_prompt(include_enrich, lang)
    pdf_data_url = pdf_base64 = None
    source_rowcount = None

    if ext == "pdf":
        b64 = base64.b64encode(file_bytes).decode("ascii")
        pdf_base64 = b64
        pdf_data_url = "data:application/pdf;base64," + b64
        source = "pdf"
    else:
        from .excelio import read_tabular
        aoa = read_tabular(file_bytes, filename)
        source_rowcount = len(aoa)
        text_prompt += "\n\nINVOICE TABLE (tab-separated rows):\n" + \
            "\n".join("\t".join("" if c is None else str(c) for c in r) for r in aoa)
        source = f"excel ({len(aoa)} rows)"

    use_search = include_enrich and web_enrich
    out = ai_call(provider, key, model, text_prompt=text_prompt,
                  pdf_data_url=pdf_data_url, pdf_base64=pdf_base64,
                  use_search=use_search, json_mode=True)

    parsed = parse_json(out["text"])
    if not parsed or "rows" not in parsed:
        raise ValueError("Could not parse JSON rows from the model output. "
                         "See the raw response in the debug panel.")
    rows = parsed["rows"]
    _apply_supplier(rows, supplier_override)

    warnings = validate_rows(rows, source_rowcount)
    debug = {"raw": (out["text"] or "")[:20000], "usage": out["usage"],
             "n_search": out["n_search"], "source": source, "prompt_chars": len(text_prompt)}
    return {"rows": rows, "warnings": warnings, "debug": debug}


def _apply_supplier(rows, supplier_override):
    sup = (supplier_override or "").strip()
    if sup:
        for r in rows:
            r["supplier"] = sup
