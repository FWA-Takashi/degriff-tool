# -*- coding: utf-8 -*-
"""Deterministic mappings and small helpers (no AI, no I/O).

Ported 1:1 from the original in-HTML JavaScript so behaviour is unchanged.
"""
import re

# Excel number formats (same as the old SheetJS build)
EUR_FMT = '0.00" €"'      # 2.75 €
EUR0_FMT = '#,##0" €"'    # 8,580 €


def to_rayon(dept):
    """MEN/WOMEN/CHILDREN (any language) -> the system's French RAYON values."""
    d = str(dept or "").strip().lower()
    if re.search(r"(femme|women|woman|female|dame|w)", d) and "homme" not in d:
        return "FEMME"
    if re.search(r"(enfant|child|kid|junior)", d):
        return "ENFANT"
    if re.search(r"(homme|men|man|male|h)", d):
        return "HOMME"
    return str(dept or "").upper()


def num(v):
    """parseFloat-like: return a float, or "" when not numeric (matches old num())."""
    if v is None or v == "":
        return ""
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip().replace(",", ".")   # tolerate comma decimals
    m = re.search(r"-?\d+(\.\d+)?", s)
    if not m:
        return ""
    try:
        f = float(m.group(0))
        return int(f) if f.is_integer() else f
    except ValueError:
        return ""


def clean_url(u):
    return re.sub(r"[?&]utm_source=openai", "", u or "")
