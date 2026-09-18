"""PyMOL worker for build_panel_a.py -- run only via the PyMOL executable
(invoked as a subprocess by build_panel_a.py, not meant to be run directly).

Renders the pre-superposed two-chain structure
(chain A = phage Bcp1 YP_009031408.1, chain B = Erinnyis ello granulovirus
YP_009091875.1; superposition done outside this repo) as cartoons
in two orientations 180 degrees apart about the vertical axis, matching
Figure 4A's "front" and "back" views of the NTase fold.
"""
import json
import sys
from pymol import cmd

pdb_path, out_view1, out_view2, out_view_json = sys.argv[-4:]

GRAY = [0.514, 0.514, 0.514]     # #838383, Erinnyis ello granulovirus (chain B)
SALMON = [0.961, 0.580, 0.580]   # #F59494, phage Bcp1 (chain A)

cmd.load(pdb_path, "ntase")
cmd.hide("everything")
cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)
cmd.set("antialias", 2)
cmd.set("cartoon_fancy_helices", 0)
cmd.set("specular", 0.15)
cmd.set("ray_trace_mode", 0)

cmd.show("cartoon", "ntase")
cmd.set_color("bcp1_salmon", SALMON)
cmd.set_color("granulovirus_gray", GRAY)
cmd.color("bcp1_salmon", "chain A")
cmd.color("granulovirus_gray", "chain B")

cmd.orient("ntase")
cmd.zoom("ntase", buffer=3)

# Save this view so build_panel_d.py can align YP_009091875's AF3 model onto
# chain B here and re-use the exact same camera, keeping panels A and D in
# the same spatial orientation.
with open(out_view_json, "w") as fh:
    json.dump(list(cmd.get_view()), fh)

cmd.ray(1600, 1300)
cmd.png(out_view1, dpi=300)

cmd.turn("y", 180)
cmd.ray(1600, 1300)
cmd.png(out_view2, dpi=300)

print("DONE")
