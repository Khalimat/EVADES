"""
Build the coloured AcrIC3 / PaCas3 complex (domain-coloured PaCas3, grey
AcrIC3) and save as a PyMOL session for interactive orientation. The camera chosen there is pasted into build_panel_b.py
(USER_VIEW) for the final render.

INPUT: AcrIC3.cif. OUTPUT: panelB_interactive.pse.
Run: /Applications/PyMOL.app/Contents/bin/pymol -cq save_session.py
"""
import os
from pymol import cmd

# All inputs/outputs live next to this script (works with `pymol -cq <script>` from any cwd).
try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:                      # __file__ is undefined in some PyMOL launch modes
    BASE = os.getcwd()

# (residue range, PyMOL colour, domain name) for PaCas3 - same as build_panel_b.py.
DOMAINS = [
    ("1-216", "yellow", "HD"),
    ("217-430", "cyan", "RecA1"),
    ("431-602", "forest", "RecA2"),
    ("603-649", "lightpink", "Linker"),
    ("650-744", "magenta", "CTD"),
]

cmd.load(os.path.join(BASE, "AcrIC3.cif"), "cx")
# chain A = PaCas3 (744 aa), chain B = AcrIC3 (100 aa)

cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)
cmd.set("antialias", 2)
cmd.set("cartoon_fancy_helices", 1)
cmd.set("ray_trace_mode", 0)
cmd.set("specular", 0.15)

cmd.hide("everything", "cx")
cmd.show("cartoon", "cx")
cmd.color("grey70", "cx and chain B")

for resi, color, name in DOMAINS:
    cmd.color(color, f"cx and chain A and resi {resi}")

cmd.orient("cx")
cmd.zoom("cx", buffer=5)

out_pse = os.path.join(BASE, "panelB_interactive.pse")
cmd.save(out_pse)
print("saved", out_pse)
