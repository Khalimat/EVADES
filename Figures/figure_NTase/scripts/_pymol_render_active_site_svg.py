"""Headless PyMOL worker for build_active_site_figure.py -- not run directly.

Renders a saved session (e.g. active_site.pse) twice from its own saved camera:
  1. Clean (all labels cleared) -- the base image.
  2. Every active_blue residue's CA marked with a small uniquely-colored
     sphere (everything else hidden), THEN, separately, each residue's
     EXISTING label (whatever text/position you left it at -- dragged or
     via `set label_position`) re-shown one at a time in a unique color
     with everything else hidden.
A separate Python step (build_active_site_figure.py) finds each marker's
and each label's real on-screen pixel by color, so your manual label
placements carry over exactly into the final SVG -- no re-deriving PyMOL's
3D->2D projection math, and no automatic layout overriding your edits.

Also renders a WIDE overview (zoom to the whole protein, same rotation, same
active-site coloring) plus the same CA markers at that wider zoom, since the
tight/close-up "clean" render above is zoomed for the inset and cuts off
most of the protein -- not suitable as the panel's full-structure overview.

Usage:
  <pymol> -cq _pymol_render_active_site_svg.py -- <session.pse> <clean.png> <ca_markers.png> <label_markers.png> <positions.json> <wide_overview.png> <wide_ca_markers.png>
"""
import colorsys
import json
import sys
from pymol import cmd

pse_path, clean_png, ca_png, label_png, positions_json, wide_png, wide_ca_png = sys.argv[-7:]

AA3TO1 = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q",
    "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
    "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
    "TYR": "Y", "VAL": "V",
}

cmd.load(pse_path)  # .pse restores its own object name(s)
W, H = cmd.get_viewport()

# Read back each active_blue residue's current label text (if any) BEFORE
# clearing labels for the clean render.
active_blue_idx = cmd.get_color_index("active_blue")
collected = []
cmd.iterate("polymer.protein and name CA", "collected.append((resi, resn, color, label))",
            space={"collected": collected})
residues = [
    {"resi": int(resi), "fallback_text": f"{AA3TO1.get(resn, '?')}{resi}",
     "label": label}
    for resi, resn, color, label in collected if color == active_blue_idx
]
n = len(residues)

# ---- 1. clean render --------------------------------------------------
cmd.label("all", "")
cmd.ray(W, H)
cmd.png(clean_png, dpi=300)

# ---- 2. CA position markers --------------------------------------------
cmd.hide("everything")
info = {}
for i, r in enumerate(residues):
    resi, text = r["resi"], (r["label"] or r["fallback_text"])
    hue = i / max(n, 1)
    rr, gg, bb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    cname = f"cac_{resi}"
    cmd.set_color(cname, [rr, gg, bb])
    obj = f"camk_{resi}"
    cmd.pseudoatom(obj, selection=f"resi {resi} and name CA and polymer.protein")
    cmd.alter(obj, "vdw=1.5")  # pseudoatom defaults to vdw=0 -- invisible without this
    cmd.show("spheres", obj)
    cmd.set("sphere_scale", 0.5, obj)
    cmd.color(cname, obj)
    info[str(resi)] = {"text": text, "ca_rgb": [round(rr * 255), round(gg * 255), round(bb * 255)]}
cmd.rebuild()

cmd.ray(W, H)
cmd.png(ca_png, dpi=300)

for r in residues:
    cmd.delete(f"camk_{r['resi']}")

# ---- 3. label position markers: re-show each residue's REAL label, one
# color per residue, so its exact dragged/set position is captured as-is --
cmd.hide("everything")
cmd.show("labels", "polymer.protein")
for i, r in enumerate(residues):
    resi = r["resi"]
    text = r["label"] or r["fallback_text"]
    cmd.select(f"labsel_{resi}", f"resi {resi} and name CA and polymer.protein")
    # Step 1's cmd.label("all", "") cleared every atom's text (not its
    # label_position, which is untouched) -- always re-apply it here.
    cmd.label(f"labsel_{resi}", f'"{text}"')
    hue = i / max(n, 1)
    rr, gg, bb = colorsys.hsv_to_rgb(hue, 1.0, 0.55)  # distinguishable value from the CA pass
    cname = f"labc_{resi}"
    cmd.set_color(cname, [rr, gg, bb])
    cmd.set("label_color", cname, f"labsel_{resi}")
    info[str(resi)]["lab_rgb"] = [round(rr * 255), round(gg * 255), round(bb * 255)]

cmd.set("label_outline_color", -1)
cmd.ray(W, H)
cmd.png(label_png, dpi=300)

with open(positions_json, "w") as fh:
    json.dump(info, fh)

# ---- 4. wide overview: whole protein, same rotation, same coloring -------
cmd.hide("everything")
cmd.show("cartoon", "polymer.protein")
cmd.color("granulovirus_gray", "polymer.protein")
cmd.color("active_blue", "byres (" + " or ".join(f"resi {r['resi']}" for r in residues) + ") and polymer.protein")
cmd.show("sticks", "resn UTP")
cmd.color("magenta", "resn UTP")
cmd.show("spheres", "resn MG")
cmd.color("yellow", "resn MG")
cmd.set("sphere_scale", 0.4, "resn MG")
cmd.zoom("polymer.protein", buffer=5)  # keeps rotation, just reframes wider
cmd.ray(W, H)
cmd.png(wide_png, dpi=300)

cmd.hide("everything")
for r in residues:
    resi = r["resi"]
    obj = f"wca_{resi}"
    cmd.pseudoatom(obj, selection=f"resi {resi} and name CA and polymer.protein")
    cmd.alter(obj, "vdw=1.5")  # pseudoatom defaults to vdw=0 -- invisible without this
    cmd.show("spheres", obj)
    cmd.set("sphere_scale", 1.5, obj)  # bigger than step 2's marker: this is a much wider zoom
    cmd.color(f"cac_{resi}", obj)  # reuse the same unique colors from step 2
cmd.rebuild()
cmd.ray(W, H)
cmd.png(wide_ca_png, dpi=300)

print(f"Wrote {clean_png}, {ca_png}, {label_png}, {positions_json}, {wide_png}, {wide_ca_png} ({n} residues)")
