"""Render each model (protein cartoon + ligand sticks) coloured by per-atom pLDDT (b-factor), AlphaFold colour scheme.
Needs pymol-open-source."""
import os
from targets import TARGETS, RENDERS

import pymol
from pymol import cmd

os.makedirs(RENDERS, exist_ok=True)
pymol.finish_launching(['pymol', '-qc'])

cmd.set("ray_opaque_background", 0)
cmd.bg_color("white")
cmd.set("antialias", 2)
cmd.set("cartoon_fancy_helices", 1)
cmd.set("cartoon_highlight_color", -1)  # -1 = follow main colour, no grey stripe
cmd.set("specular", 0)

def colour_by_plddt(sel):
    cmd.color("0x0053D6", f"({sel}) and not b<90")         # very high, dark blue
    cmd.color("0x65CBF3", f"({sel}) and b<90 and not b<70")# confident, light blue
    cmd.color("0xFFDB13", f"({sel}) and b<70 and not b<50")# low, yellow
    cmd.color("0xFF7D45", f"({sel}) and b<50")             # very low, orange

for t in TARGETS:
    cmd.delete("all")
    cmd.load(t["cif"], "mol")
    cmd.hide("everything")
    cmd.show("cartoon")
    cmd.hide("cartoon", "not polymer.protein")
    cmd.show("sticks", "not polymer.protein and not solvent")
    colour_by_plddt("mol")  # ligands (sticks) too: AF3 stores per-atom pLDDT in b-factor
    cmd.orient()
    cmd.zoom("all", buffer=3)
    out_png = os.path.join(RENDERS, f"{t['name']}_pLDDT.png")
    cmd.ray(1600, 1200)
    cmd.png(out_png, dpi=300)
    print(f"rendered {out_png}")
