"""
Recreate Figure 1, Panel C with Cas8/LsCas8 in light violet (was orange, was
salmon) and the partner chain (Cas11/AcrIB4) in grey70 - matching SpyCas9's
grey in Panel D. Camera orientations were chosen interactively in PyMOL and are
stored below as VIEW_TOP / VIEW_BOTTOM. Surface shown at 0.6 transparency, same
style on both rows.

Top row:    Cas8 (8FCJ chain I) + Cas11 (8FCJ chain L)      -- native Cascade
Bottom row: LsCas8 (chain A) + AcrIB4 (chain B)              -- AF3 prediction

INPUTS (this folder): 8FCJ.cif (Cascade cryo-EM structure), AcrIB4.cif (AF3 model).
OUTPUTS: top_cas8_cas11.png, bottom_lscas8_acrib4.png (next step: compose_panel_c.py).

Run: /Applications/PyMOL.app/Contents/bin/pymol -cq panelC/build_panel_c.py
"""
import os
from pymol import cmd

# All inputs/outputs live next to this script (works with `pymol -cq <script>` from any cwd).
try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:                      # __file__ is undefined in some PyMOL launch modes
    BASE = os.getcwd()
OUT_DIR = BASE

CAS8_VIOLET = [0.72, 0.53, 0.87]
GREY70 = [0.7, 0.7, 0.7]
TRANSPARENCY = 0.6

# camera views saved after orienting the scenes interactively in PyMOL
VIEW_TOP = (
    0.3060656785964966, -0.3309518098831177, -0.8926336765289307,
    -0.15424136817455292, -0.9424823522567749, 0.2965479791164398,
    -0.9394352436065674, 0.046918198466300964, -0.3395043909549713,
    0.0, 0.0, -331.4221496582031,
    217.0745391845703, 216.8280792236328, 251.20257568359375,
    304.56353759765625, 358.27838134765625, -20.0,
)
VIEW_BOTTOM = (
    -0.29125919938087463, -0.047777507454156876, 0.955450713634491,
    0.8575348854064941, 0.4296535551548004, 0.2828965187072754,
    -0.42402854561805725, 0.9017279148101807, -0.08416881412267685,
    0.0, 0.0, -353.63018798828125,
    -0.2559623718261719, -0.8265419006347656, -0.3118782043457031,
    278.80474853515625, 428.45562744140625, -20.0,
)

cmd.set_color("cas8_violet", CAS8_VIOLET)
cmd.set_color("partner_grey", GREY70)

cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)
cmd.set("antialias", 2)
cmd.set("cartoon_fancy_helices", 1)
cmd.set("transparency", TRANSPARENCY)
cmd.set("ray_trace_mode", 0)
cmd.set("specular", 0.15)


def render(name, width=1300, height=900):
    """Ray-trace the current scene to `name` (PNG, 300 dpi) inside BASE."""
    cmd.ray(width, height)
    cmd.png(os.path.join(OUT_DIR, name), dpi=300)
    print("saved", name)


# ---------------------------------------------------------------------------
# Top row: native Cascade Cas8 (8FCJ chain I) + Cas11 (8FCJ chain L)
# ---------------------------------------------------------------------------
cmd.load(os.path.join(BASE, "8FCJ.cif"), "top")
cmd.remove("top and not chain I+L")
cmd.hide("everything", "top")
cmd.show("cartoon", "top")
cmd.show("surface", "top")
cmd.color("cas8_violet", "top and chain I")
cmd.color("partner_grey", "top and chain L")
cmd.set_view(VIEW_TOP)
render("top_cas8_cas11.png")
cmd.delete("top")

# ---------------------------------------------------------------------------
# Bottom row: AF3 LsCas8 (chain A) + AcrIB4 (chain B)
# ---------------------------------------------------------------------------
cmd.load(os.path.join(BASE, "AcrIB4.cif"), "bottom")
cmd.hide("everything", "bottom")
cmd.show("cartoon", "bottom")
cmd.show("surface", "bottom")
cmd.color("cas8_violet", "bottom and chain A")
cmd.color("partner_grey", "bottom and chain B")
cmd.set_view(VIEW_BOTTOM)
render("bottom_lscas8_acrib4.png")

print("DONE")
