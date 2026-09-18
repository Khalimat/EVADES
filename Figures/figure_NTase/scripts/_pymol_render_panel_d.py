"""PyMOL worker for build_panel_d.py -- run only via the PyMOL executable
(invoked as a subprocess by build_panel_d.py, not meant to be run directly).

Renders the AF3 model of YP_009091875.1 (Erinnyis ello granulovirus NTase)
bound to UTP-UTP-3xMg2+ (the best-ranked seed/sample by AF3's own
ranking_score; see build_panel_d.py): a full-protein overview with the
active-site region boxed, and a tight active-site-only close-up with the
contacting residues labelled.

The AF3 model's protein chain is first structurally aligned onto chain B
(YP_009091875.1) of the same pre-superposed structure used for panel A, and
the overview re-uses panel A's saved camera (Figure/_panelA_view.json,
rotation only -- cmd.zoom reframes it for this single chain), so panel D
sits in the same spatial orientation as panel A rather than an independently
auto-oriented view.

Active-site residues = exactly panel B's 14 scored motif positions for
YP_009091875.1 (the blue/red match/mismatch calls behind its "10/14" -- see
scripts/build_panel_b.py), not a distance-to-ligand cutoff, so what's
highlighted here always matches panel B's motif calls one-to-one.
"""
import json
import sys
import numpy as np
from pymol import cmd

cif_path, superposed_pdb, view_json, out_overview, out_zoom = sys.argv[-5:]

GRAY = [0.514, 0.514, 0.514]
BLUE = [0.0, 0.0, 0.827]

RESI_TO_LETTER = {9: "G", 10: "S", 12: "A", 13: "K", 14: "G", 15: "Y", 20: "S",
                   21: "D", 23: "D", 86: "N", 87: "P", 89: "L", 90: "G", 91: "V"}
LABEL_RESIDUES = {resi: f"{letter}{resi}" for resi, letter in RESI_TO_LETTER.items()}

cmd.load(cif_path, "m")
cmd.remove("not alt ''+A")
cmd.alter("all", "alt=''")
cmd.hide("everything")
cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)
cmd.set("antialias", 2)
cmd.set("cartoon_fancy_helices", 0)
cmd.set("specular", 0.15)
cmd.set("ray_trace_mode", 0)
cmd.set("label_color", "black")
cmd.set("label_outline_color", "white")
cmd.set("label_font_id", 7)  # serif

cmd.set_color("granulovirus_gray", GRAY)
cmd.set_color("active_blue", BLUE)

# Put the AF3 model in the same coordinate frame panel A's camera was saved
# in, by aligning onto the same reference chain panel A uses.
cmd.load(superposed_pdb, "ref")
cmd.align("m and polymer.protein", "ref and chain B and polymer.protein")
cmd.delete("ref")

cmd.select("prot", "m and polymer.protein")
cmd.select("lig", "m and resn UTP")
cmd.select("ions", "m and resn MG")
resi_expr = "+".join(str(r) for r in RESI_TO_LETTER)
cmd.select("active_site", f"prot and resi {resi_expr}")

cmd.show("cartoon", "prot")
cmd.color("granulovirus_gray", "prot")
cmd.color("active_blue", "active_site")

cmd.show("sticks", "lig")
cmd.color("magenta", "lig")

cmd.show("spheres", "ions")
cmd.color("yellow", "ions")
cmd.set("sphere_scale", 0.4, "ions")

cmd.show("sticks", "active_site and not name C+N+O")

# Mg2+ direct coordination only (tight cutoff -> a handful of short, clean
# dashes at each ion, rather than every ligand...active-site polar contact --
# the latter is dozens of pairs and unreadable at this scale; the original
# figure's exact H-bond picks weren't recorded, so this keeps only the
# unambiguous, geometrically obvious ones).
cmd.distance("contacts", "ions", "(lig or active_site) and elem O+N", cutoff=2.6, mode=0)
cmd.hide("labels", "contacts")
cmd.color("yellow", "contacts")

with open(view_json) as fh:
    saved_view = json.load(fh)
cmd.set_view(saved_view)
cmd.zoom("prot", buffer=5)

cmd.ray(1400, 2000)
cmd.png(out_overview, dpi=300)

# ---- active-site-only close-up -------------------------------------------
# Full opacity everywhere (no distance-based fading): fading a residue's
# cartoon segment while its sequence neighbors stay fully faded made short
# loops (e.g. around H49) look visually detached from the rest of the
# backbone, since the connecting tube became nearly invisible against white.
# The tight zoom below already isolates the active site; that's enough.

cmd.set("label_size", 10)

# Fan labels out in SCREEN space so residues that happen to sit on the same
# side of the pocket (K13/Y15/S10/K139 are all within a few Angstrom of each
# other here) get staggered onto concentric rings instead of stacking.
# Rotation is unchanged since set_view above, so it's still valid to read.
right = np.array(saved_view[0:3])
up = np.array(saved_view[3:6])
center = np.array(cmd.centerofmass("lig or ions"))

items = []
for resi, text in LABEL_RESIDUES.items():
    sel = f"active_site and resi {resi} and name CA"
    if cmd.count_atoms(sel) == 0:
        continue
    pos = np.array(cmd.get_atom_coords(sel))
    rel = pos - center
    x, y = float(np.dot(rel, right)), float(np.dot(rel, up))
    angle = np.arctan2(y, x)
    items.append([sel, text, angle])

items.sort(key=lambda it: it[2])
BASE_R, RING_STEP, MIN_SEP = 1.6, 1.3, np.radians(45)
tier = 0
for i, it in enumerate(items):
    if i > 0 and (it[2] - items[i - 1][2]) < MIN_SEP:
        tier += 1
    else:
        tier = 0
    it.append(tier)

max_r = BASE_R + max(it[3] for it in items) * RING_STEP
cmd.zoom("lig or ions", buffer=max_r + 2.5)

for sel, text, angle, tier in items:
    r = BASE_R + tier * RING_STEP
    offset = right * (np.cos(angle) * r) + up * (np.sin(angle) * r)
    cmd.set("label_position", tuple(offset), sel)
    cmd.label(sel, f'"{text}"')

cmd.ray(2200, 2200)
cmd.png(out_zoom, dpi=300)

print("DONE")
