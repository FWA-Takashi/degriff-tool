### Example A — Excel size-grid (per-size quantities → ONE ROW PER SIZE, per colour)

INPUT (excerpt of a spreadsheet; the "HOMME" line is a section header, not a product):
```
HOMME
photo	ref	ref	pvp	codebarre	COLOR	S	M	L	TOTAL
	POLO PIQUE	PL200	49		BLACK	2	3	2	7
		PL200	49		NAVY	1	2	1	4
```

CORRECT OUTPUT (BLACK and NAVY each split into one row per size that has qty>0; pvp is a RETAIL price so it goes to pvc, paht stays empty; ref_frs = PL200; dept from the HOMME section header):
```json
{"rows":[
{"no":1,"supplier":"","brand":"","designation":"POLO PIQUE","season":"All-Year","year":"","dept":"MEN","cat_family":"POLO","size":"S","color":"BLACK","ref_n1":"","ref_frs":"PL200","total_qty":2,"colisage":"","paht":"","pvc":49,"currency":"EUR","barcode":""},
{"no":2,"supplier":"","brand":"","designation":"POLO PIQUE","season":"All-Year","year":"","dept":"MEN","cat_family":"POLO","size":"M","color":"BLACK","ref_n1":"","ref_frs":"PL200","total_qty":3,"colisage":"","paht":"","pvc":49,"currency":"EUR","barcode":""},
{"no":3,"supplier":"","brand":"","designation":"POLO PIQUE","season":"All-Year","year":"","dept":"MEN","cat_family":"POLO","size":"L","color":"BLACK","ref_n1":"","ref_frs":"PL200","total_qty":2,"colisage":"","paht":"","pvc":49,"currency":"EUR","barcode":""},
{"no":4,"supplier":"","brand":"","designation":"POLO PIQUE","season":"All-Year","year":"","dept":"MEN","cat_family":"POLO","size":"S","color":"NAVY","ref_n1":"","ref_frs":"PL200","total_qty":1,"colisage":"","paht":"","pvc":49,"currency":"EUR","barcode":""},
{"no":5,"supplier":"","brand":"","designation":"POLO PIQUE","season":"All-Year","year":"","dept":"MEN","cat_family":"POLO","size":"M","color":"NAVY","ref_n1":"","ref_frs":"PL200","total_qty":2,"colisage":"","paht":"","pvc":49,"currency":"EUR","barcode":""},
{"no":6,"supplier":"","brand":"","designation":"POLO PIQUE","season":"All-Year","year":"","dept":"MEN","cat_family":"POLO","size":"L","color":"NAVY","ref_n1":"","ref_frs":"PL200","total_qty":1,"colisage":"","paht":"","pvc":49,"currency":"EUR","barcode":""}
]}
```
Note: the TOTAL column (7, 4) is NOT emitted as its own row — it must equal the sum of that colour's per-size quantities. There is no barcode in this document, so barcode stays "".
