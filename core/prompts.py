# -*- coding: utf-8 -*-
"""Prompt assembly. The human-editable instruction text lives in ../prompts/*.md
so it can be tuned without touching code. This module only wires the pieces
together and appends the few-shot examples.
"""
import os

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")


def _read(rel):
    with open(os.path.join(PROMPTS_DIR, rel), encoding="utf-8") as f:
        return f.read().strip()


def _load_examples():
    """Concatenate every prompts/examples/*.md (sorted) as few-shot guidance.
    Add or edit a file there to change accuracy — no code change needed."""
    ex_dir = os.path.join(PROMPTS_DIR, "examples")
    if not os.path.isdir(ex_dir):
        return ""
    blocks = []
    for name in sorted(os.listdir(ex_dir)):
        if name.lower().endswith(".md"):
            blocks.append(_read(os.path.join("examples", name)))
    if not blocks:
        return ""
    return ("\n\nSTUDY THESE WORKED EXAMPLES CAREFULLY, then apply the same rules to the "
            "real document (do not copy the example data into your answer):\n\n"
            + "\n\n".join(blocks))


# Canonical field list emitted by extraction (order is documentation only; JSON is unordered)
_FIELDS = ('"no":..,"supplier":..,"brand":..,"designation":..,"season":..,"year":..,"dept":..,'
           '"cat_family":..,"size":..,"color":..,"ref_n1":..,"ref_frs":..,"total_qty":..,'
           '"colisage":..,"paht":..,"pvc":..,"currency":..,"barcode":..')


def build_extract_prompt(include_enrich=False, lang="en", use_examples=True):
    """Faithful port of the old buildExtractPrompt(), with the instruction body
    now read from prompts/extract_system.md and few-shot examples appended."""
    fr = lang == "fr"
    unknown_color = "Non spécifié" if fr else "Not specified"
    head = _read("extract_system.md").replace("{UNKNOWN_COLOR}", unknown_color)

    enrich_line = ""
    fields = _FIELDS
    if include_enrich:
        lang_word = "FRENCH" if fr else "ENGLISH"
        enrich_line = (f"\n\nENRICHMENT: for each row add enriched_data = 2-3 sentences on "
                       f"material, unique features, and target market, written in {lang_word}.")
        fields = _FIELDS + ',"enriched_data":..'

    examples = _load_examples() if use_examples else ""

    return (head + enrich_line + examples +
            "\n\nOutput STRICT JSON ONLY (no markdown, no prose, no code fences). "
            "One object per product line:\n{\"rows\":[{" + fields + "}]}")


def build_bench_prompt(p):
    """Faithful port of benchPrompt(). p is a dict with brand/designation/ean/color/size."""
    ident = " ".join(x for x in [p.get("brand"), p.get("designation")] if x)
    ean = f" — barcode/EAN: {p['ean']}" if p.get("ean") else ""
    extra_parts = [x for x in [p.get("color"), p.get("size")] if x]
    extra = f" ({', '.join(extra_parts)})" if extra_parts else ""
    tmpl = _read("benchmark.md")
    return (tmpl.replace("{PRODUCT_ID}", ident)
                .replace("{EAN}", ean)
                .replace("{EXTRA}", extra))
