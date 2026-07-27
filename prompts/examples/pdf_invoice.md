### Example B — PDF/paper invoice line (brand after the slash; skip fee lines; combined size range)

INPUT (excerpt of an invoice; the last line is a transport fee, NOT a product):
```
Réf.            Désignation                         Tailles        Qté   PA HT
RAOUL/REDSKINS  TEE SHIRT COL ROND RAOUL homme      S à XXL        120   4,50
3690JOLANO/CHEVIGNON  TEE SHIRT HOMME COL ROND      S/M/L/XL/XXL   200   3,90
PARTICIPATION FRAIS DE TRANSPORT                                    1     35,00
```

CORRECT OUTPUT (brand = token AFTER the slash; ref_frs = token BEFORE the slash; PA HT is a purchase price → paht; comma decimal → dot; the transport line is skipped; sizes given as a single combined range → ONE row with that range):
```json
{"rows":[
{"no":1,"supplier":"","brand":"REDSKINS","designation":"TEE SHIRT COL ROND RAOUL homme","season":"SS","year":"","dept":"MEN","cat_family":"T-SHIRT","size":"S à XXL","color":"Not specified","ref_n1":"","ref_frs":"RAOUL","total_qty":120,"colisage":"","paht":4.50,"pvc":"","currency":"EUR","barcode":""},
{"no":2,"supplier":"","brand":"CHEVIGNON","designation":"TEE SHIRT HOMME COL ROND","season":"SS","year":"","dept":"MEN","cat_family":"T-SHIRT","size":"S/M/L/XL/XXL","color":"Not specified","ref_n1":"","ref_frs":"3690JOLANO","total_qty":200,"colisage":"","paht":3.90,"pvc":"","currency":"EUR","barcode":""}
]}
```
Note: "PARTICIPATION FRAIS DE TRANSPORT" is a shipping fee, so it produces NO row. paht holds the purchase price (PA HT); pvc stays empty because no retail price is shown.
