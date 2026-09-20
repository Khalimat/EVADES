#!/usr/bin/env python3
"""Copy the models used in the figure out of the raw AlphaFold Server output.

Reads inputs/selected_models.tsv (top-ranked model per substrate x seed, plus the overall
best per substrate) and writes models/<substrate>_seed<N>.cif and models/<substrate>_best.cif.
The table is the record of the selection: the server summary JSONs only carry ranking scores
rounded to 2 decimals, so ties cannot be re-broken from the files shipped here.

Run:  python3 scripts/01_select_models.py
"""
import csv, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "models")
os.makedirs(OUT, exist_ok=True)

n = 0
for r in csv.DictReader(open(os.path.join(ROOT, "inputs", "selected_models.tsv")), delimiter="\t"):
    src = os.path.join(ROOT, r["raw_model"])
    shutil.copyfile(src, os.path.join(OUT, f"{r['substrate']}_seed{r['seed']}.cif"))
    n += 1
    if r["best_overall"] == "1":
        shutil.copyfile(src, os.path.join(OUT, f"{r['substrate']}_best.cif"))
        n += 1
print(f"wrote {n} model files to {OUT}")
