# -*- coding: utf-8 -*-
"""DEMO-mode sample data (no API calls). Ported from the old JS."""
from .rules import to_rayon


def extract_rows():
    return [
        {"no": 1, "supplier": "ETS MICHEL", "brand": "CHEVIGNON",
         "designation": "TEE SHIRT HOMME COL ROND JOLANO 3690", "season": "All-Year", "year": "2026",
         "dept": "HOMME", "cat_family": "TEE SHIRT", "size": "S / M / L / XL / XXL", "color": "Not specified",
         "ref_n1": "", "ref_frs": "JOLANO", "total_qty": 3120,
         "enriched_data": "(DEMO) Crew-neck cotton-jersey men's tee with embroidered chest logo. Classic French heritage casualwear, all-season.",
         "paht": 2.75, "barcode": "3700307301615"},
        {"no": 2, "supplier": "ETS MICHEL", "brand": "KAPORAL",
         "designation": "BOXER X5 EN BOITE / ALY", "season": "All-Year", "year": "2026",
         "dept": "HOMME", "cat_family": "UNDERWEAR", "size": "Various", "color": "Multiple",
         "ref_n1": "", "ref_frs": "ALY", "total_qty": 2520,
         "enriched_data": "(DEMO) Pack of five men's boxers in a gift box, cotton-elastane blend, classic fit.",
         "paht": 5.5, "barcode": "3700307345428"},
        {"no": 3, "supplier": "ETS MICHEL", "brand": "BURTON",
         "designation": "LEGGING EFFET JEANS FOURRE ANALIA", "season": "FW", "year": "2026",
         "dept": "FEMME", "cat_family": "BOTTOMS", "size": "Various", "color": "Jean effect",
         "ref_n1": "", "ref_frs": "ANALIA", "total_qty": 1680,
         "enriched_data": "(DEMO) Fleece-lined jean-effect leggings, stretch fabric, casual everyday wear.",
         "paht": 4.73, "barcode": "3700307345466"},
    ]


def bench_rows():
    base = extract_rows()
    px = [[35, 35, 35, "chevignon.fr ; laredoute.fr"],
          [25, 30, 20, "brandalley.fr ; veepee.fr"],
          [15, 20, 10, "modz.fr ; stokomani.fr"]]
    out = []
    for i, r in enumerate(base):
        out.append({"no": r["no"], "rayon": to_rayon(r["dept"]), "model": (r.get("ref_frs") or "").split("/")[0],
                    "ean": r["barcode"], "designation": r["designation"], "qty": r["total_qty"], "paht": r["paht"],
                    "price_avg": px[i][0], "price_high": px[i][1], "price_low": px[i][2],
                    "benchmarking_reference": px[i][3]})
    return out
