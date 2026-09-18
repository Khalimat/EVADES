"""
Recreate Figure 1, Panel B: AcrIC3 vs Pseudomonas aeruginosa Cas3 (PaCas3).

Per the methods, domain boundaries transferred from Thermobifida fusca Cas3
(PDB 4QQZ) onto PaCas3 (744 aa, matches chain A exactly):
  1-216 HD, 217-430 RecA1, 431-602 RecA2, 603-649 Linker, 650-744 CTD
AcrIC3 = chain B (100 aa).

INPUT: AcrIC3.cif (AF3 model, chain A = PaCas3, chain B = AcrIC3).
OUTPUT: PanelB_render.png (next steps: build_domain_bar.py, compose_panel_b.py).

Run: /Applications/PyMOL.app/Contents/bin/pymol -cq panelB/build_panel_b.py
"""
import os
from pymol import cmd

# All inputs/outputs live next to this script (works with `pymol -cq <script>` from any cwd).
try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:                      # __file__ is undefined in some PyMOL launch modes
    BASE = os.getcwd()

# (residue range, PyMOL colour, domain name) for PaCas3.
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

# AcrIC3 (chain B) grey; each PaCas3 (chain A) domain in its own colour.
cmd.hide("everything", "cx")
cmd.show("cartoon", "cx")
cmd.color("grey70", "cx and chain B")

for resi, color, name in DOMAINS:
    cmd.color(color, f"cx and chain A and resi {resi}")

USER_VIEW = (
    -0.611874520778656, -0.5119099617004395, 0.6029593348503113,
    0.4881511330604553, -0.8442177176475525, -0.22136932611465454,
    0.6223472952842712, 0.15888454020023346, 0.7664418816566467,
    0.0, 0.0, -298.7800598144531,
    -2.361095428466797, 1.1245613098144531, 1.7888145446777344,
    275.0692443847656, 322.49078369140625, -20.0,
)
cmd.set_view(USER_VIEW)  # camera saved after orienting the scene interactively in PyMOL

cmd.ray(1600, 1200)
cmd.png(os.path.join(BASE, "PanelB_render.png"), dpi=300)
print("saved PanelB_render.png")
print("DONE")
