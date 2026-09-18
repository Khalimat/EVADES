"""Latch renders for Figure 3 — headless PyMOL.

The OB-domain 'latch' beta-hairpin (Chlorella-virus DNA ligase residues 202-231;
Nair et al. 2007) is the structural element that lets the minimal ligase sense
nicks without accessory domains.  Two views, from the FATCAT superposition
(data/structures/orf55_on_2q2u_FATCAT.pdb: chain A = ligase, chain B = ORF55):

  context_1.png / context_2.png   the whole superimposed enzymes — ORF55 (coral)
                                  and the Chlorella-virus ligase (grey) — with the
                                  latch of both highlighted in gold; two 90-deg views
  zoom.png                        the latch magnified: ORF55 latch (coral) over the
                                  Chlorella-virus ligase latch (grey), with the
                                  DNA-gripping side chains as sticks

Run:  /Applications/PyMOL.app/Contents/bin/pymol -cq scripts/04_render_latch.py
"""
import os
import sys
from pymol import cmd

for _c in (os.path.join(os.getcwd(), "scripts"),):
    if os.path.exists(os.path.join(_c, "figconfig.py")):
        sys.path.insert(0, _c)
        break
import figconfig as cfg

ROOT = os.path.dirname(sys.path[0]) if os.path.basename(sys.path[0]) == "scripts" else os.getcwd()
STRUCT = os.path.join(ROOT, "data", "structures")
OUT = os.path.join(ROOT, "figures", "latch")
os.makedirs(OUT, exist_ok=True)

LATCH = "202-231"                 # Chlorella-virus ligase latch (Nair et al. 2007)
CONTACT = "206+217+220+221+223"   # DNA-gripping residues (Asn206, Tyr/Arg217, Arg220, Ser221, His223)

cmd.bg_color("white")
cmd.set("ray_opaque_background", 0)
cmd.set("antialias", 2)
cmd.set("ray_trace_mode", 0)
cmd.set("ray_shadows", 0)
cmd.set("ambient", 0.40)
cmd.set("direct", 0.55)
cmd.set("specular", 0.18)
cmd.set("shininess", 13)
cmd.set("depth_cue", 0)
cmd.set("cartoon_fancy_helices", 1)
cmd.set("cartoon_flat_sheets", 1)
cmd.set("cartoon_smooth_loops", 1)
cmd.set("cartoon_transparency", 0.0)

cmd.set_color("coral", list(cfg.ORF55_COLOR))
cmd.set_color("liggrey", list(cfg.LIGASE_COLOR))
cmd.set_color("latchgold", [0.878, 0.639, 0.169])   # #E0A32B  distinct from coral/grey/blue

cmd.load(os.path.join(STRUCT, "orf55_on_2q2u_FATCAT.pdb"), "sup")   # A=ligase B=ORF55
LIG = "sup and chain A"
ORF = "sup and chain B"

# ------------------------------------------------- context : whole enzymes ----
cmd.hide("everything")
cmd.show("cartoon", "sup")
cmd.color("liggrey", LIG)
cmd.color("coral", ORF)
cmd.color("latchgold", f"(({LIG}) or ({ORF})) and resi {LATCH}")

cmd.orient("sup")
cmd.turn("y", -15)
cmd.turn("x", 5)
cmd.zoom("sup", buffer=2, complete=1)
v = cmd.get_view()
for i, ty in enumerate((0, 90), start=1):
    cmd.set_view(v)
    if ty:
        cmd.turn("y", ty)
    cmd.ray(1300, 1500)
    cmd.png(os.path.join(OUT, f"context_{i}.png"), dpi=300)
    print("wrote", f"context_{i}.png")

# ------------------------------------------------- zoom : the latch itself ----
cmd.hide("everything")
lig_l = f"{LIG} and resi 200-234"
orf_l = f"{ORF} and resi 200-234"
cmd.show("cartoon", f"({lig_l}) or ({orf_l})")
cmd.set("cartoon_transparency", 0.15, f"({lig_l}) or ({orf_l})")
cmd.color("liggrey", lig_l)
cmd.color("coral", orf_l)
sticks = f"(({LIG}) or ({ORF})) and resi {CONTACT}"
cmd.show("sticks", sticks)
cmd.set("stick_radius", 0.16, sticks)
cmd.color("liggrey", f"({LIG}) and resi {CONTACT}")
cmd.color("coral", f"({ORF}) and resi {CONTACT}")

cmd.orient(f"({lig_l}) or ({orf_l})")
cmd.turn("y", 20)
cmd.turn("x", -10)
cmd.zoom(f"({lig_l}) or ({orf_l})", buffer=1.5, complete=1)
cmd.ray(1500, 1150)
cmd.png(os.path.join(OUT, "zoom.png"), dpi=300)
print("wrote zoom.png")
print("Latch renders done.")
