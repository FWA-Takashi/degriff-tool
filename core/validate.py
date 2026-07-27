# -*- coding: utf-8 -*-
"""Deterministic post-extraction checks. These do NOT change the data — they
surface likely accuracy problems as human-readable warnings for the debug panel,
so a low-quality extraction is visible instead of silently shipped.
"""
from .rules import num, to_rayon

REQUIRED = ["designation"]              # a row with no designation is meaningless
KNOWN_RAYON = {"HOMME", "FEMME", "ENFANT"}
# our own company / buyer aliases — these must NEVER appear as the supplier
BUYER_ALIASES = ["degriffstock", "degriff stock", "dégriffstock", "achat international",
                 "france achat", "fai"]


def validate_rows(rows, source_rowcount=None):
    warnings = []
    if not rows:
        return ["No rows were extracted."]

    # supplier sanity (the #1 confusion: buyer vs vendor)
    sup = str(rows[0].get("supplier", "") or "").strip()
    if not sup:
        warnings.append("supplier is empty — set it with the 'Supplier (optional override)' field if the "
                        "document names a vendor.")
    elif any(a in sup.lower() for a in BUYER_ALIASES):
        warnings.append(f"supplier = '{sup}' looks like the BUYER (our company), not the issuing vendor — "
                        "fix the supplier (it must be the company that issued the invoice).")

    for i, r in enumerate(rows, start=1):
        label = f"row {i}"
        for f in REQUIRED:
            if not str(r.get(f, "")).strip():
                warnings.append(f"{label}: required field '{f}' is empty.")
        # qty should be a positive number
        q = num(r.get("total_qty"))
        if q == "" or (isinstance(q, (int, float)) and q <= 0):
            warnings.append(f"{label} ({_short(r)}): total_qty is missing or not > 0.")
        # a price should be present somewhere (paht or pvc)
        if num(r.get("paht")) == "" and num(r.get("pvc")) == "":
            warnings.append(f"{label} ({_short(r)}): no price (both paht and pvc empty).")
        # paht must be numeric if present
        if str(r.get("paht", "")).strip() and num(r.get("paht")) == "":
            warnings.append(f"{label} ({_short(r)}): paht is not numeric: {r.get('paht')!r}.")
        # dept should map to a known rayon
        if str(r.get("dept", "")).strip() and to_rayon(r.get("dept")) not in KNOWN_RAYON:
            warnings.append(f"{label} ({_short(r)}): dept '{r.get('dept')}' did not map to HOMME/FEMME/ENFANT.")
        # barcode, if present, should be digits
        bc = str(r.get("barcode", "") or "").strip()
        if bc and not bc.isdigit():
            warnings.append(f"{label} ({_short(r)}): barcode is not all digits: {bc!r}.")

    # rough completeness hint for spreadsheets (source has many rows, few extracted)
    if source_rowcount and source_rowcount > 20 and len(rows) < source_rowcount * 0.3:
        warnings.append(f"Only {len(rows)} rows extracted from a {source_rowcount}-row sheet — "
                        "possible early stop/truncation. Consider a stronger model for large grids.")
    return warnings


def _short(r):
    d = str(r.get("designation", "") or "")[:24]
    c = str(r.get("color", "") or "")
    s = str(r.get("size", "") or "")
    tail = " ".join(x for x in [c, s] if x)
    return (d + (" · " + tail if tail else "")).strip() or "?"
