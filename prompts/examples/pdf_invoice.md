### Example B — PDF/paper invoice line (brand vs model, full supplier ref, no colour from title, French family, skip fees)

INPUT (excerpt of an invoice; there is NO colour column; the last line is a transport fee, NOT a product):
```
Réf.                  Désignation                          Tailles        Qté   PA HT
RAOUL/REDSKINS        TEE SHIRT COL ROND RAOUL homme       S à XXL        120   4,50
3690/JOLANO/CHEVIGNON TEE SHIRT HOMME COL ROND CANARD      S/M/L/XL/XXL   200   3,90
PARTICIPATION FRAIS DE TRANSPORT                                           1     35,00
```

CORRECT OUTPUT:
- ref_frs = the FULL reference exactly as printed ("RAOUL/REDSKINS", "3690/JOLANO/CHEVIGNON") — this is REF FOURNISSEUR.
- brand = the recognizable BRAND NAME (REDSKINS; CHEVIGNON) — never the model code (RAOUL, JOLANO, 3690). ref_n1 stays "".
- cat_family = "TEE SHIRT" (as written, French) — NOT the English "T-SHIRT".
- color = "Not specified": the word "CANARD" appears only inside the designation text, and there is no colour column, so DO NOT extract it as a colour.
- PA HT is a purchase price → paht (comma decimal → dot). The transport line produces NO row. Combined size range → ONE row.
```json
{"rows":[
{"no":1,"supplier":"","brand":"REDSKINS","designation":"TEE SHIRT COL ROND RAOUL homme","season":"SS","year":"","dept":"MEN","cat_family":"TEE SHIRT","size":"S à XXL","color":"Not specified","ref_n1":"","ref_frs":"RAOUL/REDSKINS","total_qty":120,"colisage":"","paht":4.50,"pvc":"","currency":"EUR","barcode":""},
{"no":2,"supplier":"","brand":"CHEVIGNON","designation":"TEE SHIRT HOMME COL ROND CANARD","season":"SS","year":"","dept":"MEN","cat_family":"TEE SHIRT","size":"S/M/L/XL/XXL","color":"Not specified","ref_n1":"","ref_frs":"3690/JOLANO/CHEVIGNON","total_qty":200,"colisage":"","paht":3.90,"pvc":"","currency":"EUR","barcode":""}
]}
```
Note: "PARTICIPATION FRAIS DE TRANSPORT" is a shipping fee → no row. "CANARD" is a colour word but it is only in the title, so color stays "Not specified".
