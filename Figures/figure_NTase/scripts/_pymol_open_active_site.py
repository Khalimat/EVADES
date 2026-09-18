"""Open the Panel D active-site scene interactively in PyMOL, from scratch.

What this does:
  1. Loads the AF3 model of YP_009091875.1 (Erinnyis ello granulovirus NTase)
     bound to UTP-UTP-3xMg2+ (best-ranked seed/sample; picked by
     open_active_site_pymol.py via build_panel_d.find_best_model()).
  2. Aligns its protein chain onto chain B (YP_009091875.1) of the same
     pre-superposed structure used for panel A, then loads panel A's saved
     camera (Figure/_panelA_view.json) so this sits in the same spatial
     orientation as panel A instead of an independently auto-oriented view.
  3. Colors: gray protein, magenta ligand, yellow Mg2+, blue active-site
     residues -- defined by actually detecting bonds to the ligand/ions
     (matching the manuscript text: "residues forming bonds with NTPs and
     ions"), not a plain distance-to-anything cutoff and not panel B's
     motif list: Mg2+ inner-sphere coordination (protein N/O within
     MG_COORD_CUTOFF of an ion) OR a hydrogen bond to the ligand (protein
     N/O within HBOND_CUTOFF of a ligand N/O, AND passing PyMOL's
     find_pairs geometric plausibility check -- mode=1, atom orientation,
     not just distance -- at HBOND_ANGLE degrees). Distance alone (no angle
     check) also picks up K13/S20/H49, which aren't actually oriented to
     H-bond; the angle check drops them. Fully solid colors throughout (no
     by-element carbon/red-O/blue-N tinting).
  4. Full cartoon opacity throughout. (An earlier version faded the cartoon
     far from the pocket to draw focus there, but that made short loops --
     e.g. around H49 -- look visually detached from their own backbone,
     since the connecting tube to their faded neighbors became nearly
     invisible against white. Not worth the artifact; the zoom you do
     interactively already isolates the active site.)
  5. No labels by default -- add your own via `label <selection>, "<text>"`,
     e.g. `label active_site and resi 49 and name CA, "H49"`.

Not run directly -- launched by open_active_site_pymol.py, which finds the
current best AF3 model/paths and calls:
  <pymol> scripts/_pymol_open_active_site.py -- <cif> <superposed_pdb> <view_json>

To run by hand instead:
  /Applications/PyMOL.app/Contents/bin/pymol scripts/_pymol_open_active_site.py -- \\
      path/to/model.cif structures/ntase_YP_009091875.pdb Figure/_panelA_view.json
"""
import json
import sys
from pymol import cmd

cif_path, superposed_pdb, view_json = sys.argv[-3:]

GRAY = [0.514, 0.514, 0.514]
BLUE = [0.0, 0.0, 0.827]

MG_COORD_CUTOFF = 2.6   # protein N/O within this of a Mg2+ ion = direct coordination
HBOND_CUTOFF = 3.5      # protein N/O within this of a ligand N/O = candidate hydrogen bond
HBOND_ANGLE = 45.0      # ...and passing this atom-orientation check (find_pairs mode=1)

cmd.load(cif_path, "m")
cmd.remove("not alt ''+A")
cmd.alter("all", "alt=''")
cmd.rebond("m")  # recompute bonds after the alt-loc edits above, so nothing
                 # looks disconnected when shown as sticks
cmd.hide("everything")
cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)
cmd.set("antialias", 2)
cmd.set("cartoon_fancy_helices", 0)
cmd.set("specular", 0.15)
cmd.set("cartoon_transparency", 0.0)
cmd.set("depth_cue", 0)  # otherwise far-side geometry fades toward white
cmd.set("label_color", "black")
cmd.set("label_outline_color", -1)  # no halo
cmd.set("label_font_id", 7)  # serif
cmd.set("label_size", 18)

cmd.set_color("granulovirus_gray", GRAY)
cmd.set_color("active_blue", BLUE)

# Align onto panel A's reference chain, then borrow its saved camera, so
# this scene sits in the same spatial orientation as panel A.
cmd.load(superposed_pdb, "ref")
cmd.align("m and polymer.protein", "ref and chain B and polymer.protein")
cmd.delete("ref")

cmd.select("prot", "m and polymer.protein")
cmd.select("lig", "m and resn UTP")
cmd.select("ions", "m and resn MG")

cmd.select("mg_coord", f"byres ((prot and elem N+O) within {MG_COORD_CUTOFF} of ions)")

# Geometry-aware H-bonds: find_pairs mode=1 checks atom orientation (not just
# distance), dropping pairs that are close but not actually aimed at each
# other. It doesn't check element type itself (see its docstring), hence the
# elem N+O pre-filter on both sides.
hbond_pairs = cmd.find_pairs("prot and elem N+O", "lig and elem N+O",
                              cutoff=HBOND_CUTOFF, mode=1, angle=HBOND_ANGLE)
hbond_resis = {cmd.get_model(f"{model} and index {index}").atom[0].resi
               for prot_atom, _lig_atom in hbond_pairs
               for model, index in [prot_atom]}
if hbond_resis:
    cmd.select("hbond", "prot and resi " + "+".join(hbond_resis))
else:
    cmd.select("hbond", "none")

cmd.select("active_site", "byres (mg_coord or hbond)")
cmd.delete("mg_coord")
cmd.delete("hbond")

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
# dashes at each ion, rather than every ligand...active-site polar contact,
# which is dozens of pairs and unreadable at this scale).
cmd.distance("contacts", "ions", "(lig or active_site) and elem O+N", cutoff=2.6, mode=0)
cmd.hide("labels", "contacts")
cmd.color("yellow", "contacts")

with open(view_json) as fh:
    saved_view = json.load(fh)
cmd.set_view(saved_view)
cmd.zoom("lig or ions", buffer=10)

active_resis = sorted({int(a.resi) for a in cmd.get_model("active_site and name CA").atom})
print("Scene loaded. Objects: m (structure). Selections: prot / lig / ions / active_site.")
print(f"active_site = residues forming bonds with NTPs/ions: {active_resis}")
print('Add a label with, e.g.:  label active_site and resi 21 and name CA, "D21"')
