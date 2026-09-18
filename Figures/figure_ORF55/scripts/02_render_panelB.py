"""Panel B of Figure 3 — headless PyMOL.

For each of the 13 active-site residues of the Chlorella-virus DNA ligase
(Nair et al. 2007), render a close-up of that residue (grey sticks) overlaid
on the structurally equivalent ORF55 residue (coral sticks), read from the
FATCAT superposition (data/structures/orf55_on_2q2u_FATCAT.pdb:
chain A = ligase, chain B = ORF55).

Pairs are taken from data/active_site_residues.tsv (tab-separated; columns used:
order, label, ligase_resi, orf55_resi). Each residue is drawn as one solid colour
by source (ligase grey, ORF55 coral), not by element, so the overlap of the two
side chains is easy to judge.

Run:  /Applications/PyMOL.app/Contents/bin/pymol -cq scripts/02_render_panelB.py
Out:  figures/panelB/<label>.png   (transparent background, square)
"""
import csv
import os
import sys
from pymol import cmd

for _c in (os.path.join(os.getcwd(), "scripts"),):
    if os.path.exists(os.path.join(_c, "figconfig.py")):
        sys.path.insert(0, _c)
        break
import figconfig as cfg

ROOT   = os.path.dirname(sys.path[0])
STRUCT = os.path.join(ROOT, "data", "structures")
OUT    = os.path.join(ROOT, "figures", "panelB")
os.makedirs(OUT, exist_ok=True)

with open(os.path.join(ROOT, "data", "active_site_residues.tsv")) as fh:
    PAIRS = list(csv.DictReader(fh, delimiter="\t"))


# --------------------------------------------------------------- appearance ---
cmd.bg_color(cfg.BG_COLOR)
cmd.set("ray_opaque_background", 0)
cmd.set("antialias", 2)
cmd.set("ray_trace_mode", 0)
cmd.set("ray_shadows", 0)
cmd.set("ambient", 0.42)
cmd.set("direct", 0.58)
cmd.set("specular", 0.22)
cmd.set("shininess", 14)
cmd.set("depth_cue", 0)
cmd.set("stick_radius", 0.28)
cmd.set("stick_h_scale", 1.0)
cmd.set("valence", 0)

# Load the superposition once; chain A = ligase, chain B = ORF55.
cmd.load(os.path.join(STRUCT, "orf55_on_2q2u_FATCAT.pdb"), "sup")
cmd.hide("everything")

cmd.set_color("coral", list(cfg.ORF55_COLOR))
cmd.set_color("liggrey", [0.42, 0.42, 0.42])   # a touch darker than Panel A so it
#                                                reads under the coral in the overlay


def one(pair):
    """Render one close-up PNG: the ligase residue and its ORF55 equivalent, centred and zoomed."""
    label = pair["label"]
    li, oi = pair["ligase_resi"], pair["orf55_resi"]
    lig = f"sup and chain A and resi {li}"
    orf = f"sup and chain B and resi {oi}"
    both = f"(({lig}) or ({orf}))"

    cmd.hide("everything")
    cmd.show("sticks", both)
    cmd.color("liggrey", lig)          # each residue ONE solid colour by source
    cmd.color("coral",   orf)          # (no element colouring)

    cmd.orient(both)
    cmd.zoom(both, buffer=1.7, complete=1)
    cmd.turn("y", 8)

    out = os.path.join(OUT, f"{pair['order'].zfill(2)}_{label}.png")
    cmd.ray(cfg.INSET_PX, cfg.INSET_PX)
    cmd.png(out, dpi=300)
    print("wrote", out)


# One close-up per row of the residue table.
for p in PAIRS:
    one(p)

print("Panel B done.")
