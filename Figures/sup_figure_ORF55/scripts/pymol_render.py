"""Headless render of ORF55-DNA interface panels using the highest-confidence model per substrate.
Run:  /Applications/PyMOL.app/Contents/bin/pymol -cq scripts/pymol_render.py
Chains: A=ORF55, B=ATP, C=continuous strand, D=upstream arm (3'-OH), E=downstream arm (5'-P)."""
import os
from pymol import cmd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M   = os.path.join(REPO, "models")
OUT = os.path.join(REPO, "renders", "parts")
os.makedirs(OUT, exist_ok=True)
PANEL = ["nicked", "gap1nt", "gap2nt"]
W, H = 1500, 1500

def setup():
    cmd.reinitialize()
    cmd.bg_color("white")
    cmd.set("ray_opaque_background", 1); cmd.set("orthoscopic", 1)
    cmd.set("antialias", 2); cmd.set("ray_shadows", 1)
    cmd.set("ambient", 0.42); cmd.set("specular", 0.12)
    cmd.set("cartoon_nucleic_acid_mode", 4)
    cmd.set("cartoon_ring_mode", 3); cmd.set("cartoon_ring_finder", 1)
    cmd.set("cartoon_ring_transparency", 0.25)
    cmd.set("cartoon_tube_radius", 0.55)
    cmd.set("dash_gap", 0.3); cmd.set("dash_radius", 0.05); cmd.set("dash_color", "grey20")
    cmd.set("cartoon_transparency", 0)

def load_all_aligned():
    for u in PANEL:
        cmd.load(f"{M}/{u}_best.cif", u); cmd.hide("everything", u)
    for u in PANEL[1:]:
        cmd.align(f"{u} and chain A and name CA", f"{PANEL[0]} and chain A and name CA")

def shared_view(buf=6):
    cmd.orient(" or ".join(f"({u} and (chain A or chain C+D+E))" for u in PANEL))
    cmd.zoom(" or ".join(f"({u} and (chain A or chain C+D+E))" for u in PANEL), buffer=buf)
    return cmd.get_view()

# ---------- FIG A : best model per substrate, enzyme-DNA interface ----------
def figA(view):
    for t in PANEL:
        setup(); load_all_aligned()
        cmd.disable("all"); cmd.enable(t)
        cmd.show("cartoon", f"{t} and chain A"); cmd.color("grey75", f"{t} and chain A")
        cmd.show("surface", f"{t} and chain A"); cmd.set("transparency", 0.72, f"{t} and chain A")
        cmd.show("cartoon", f"{t} and chain C+D+E")
        cmd.color("wheat",  f"{t} and chain C")
        cmd.color("marine", f"{t} and chain D")
        cmd.color("salmon", f"{t} and chain E")
        # junction nucleotides: 3' end of upstream arm (D resi 10) + 5' end of downstream arm (E resi 1)
        cmd.select("jx", f"{t} and ((chain D and resi 10) or (chain E and resi 1))")
        cmd.show("sticks", "jx"); cmd.set("stick_radius", 0.20, "jx")
        cmd.color("red", "jx and elem C"); cmd.util.cnc("jx")
        cmd.show("sticks", f"{t} and resn ATP"); cmd.color("yellow", f"{t} and resn ATP")
        cmd.distance("hb", f"{t} and chain A and (elem N+O) and not name N",
                     f"{t} and chain C+D+E and (elem N+O)", 3.5, mode=2)
        cmd.hide("labels", "hb")
        cmd.set_view(view)
        cmd.ray(W, H); cmd.png(f"{OUT}/A_{t}.png", dpi=300)

# ---------- FIG B : best model per substrate, coloured by pLDDT (AlphaFold scheme) ----------
# AlphaFold pLDDT bins: >=90 very high, 70-90 confident, 50-70 low, <50 very low
def figB(view):
    for t in PANEL:
        setup(); load_all_aligned()
        cmd.set_color("af_vhigh", [0.051, 0.341, 0.827])   # #0D57D3
        cmd.set_color("af_conf",  [0.396, 0.796, 0.953])   # #65CBF3
        cmd.set_color("af_low",   [1.000, 0.859, 0.075])   # #FFDB13
        cmd.set_color("af_vlow",  [1.000, 0.490, 0.271])   # #FF7D45
        cmd.disable("all"); cmd.enable(t)
        sel = f"{t} and chain A+C+D+E"
        cmd.show("cartoon", sel)
        cmd.color("af_vlow",  f"({sel}) and b<50")
        cmd.color("af_low",   f"({sel}) and (not b<50) and b<70")
        cmd.color("af_conf",  f"({sel}) and (not b<70) and b<90")
        cmd.color("af_vhigh", f"({sel}) and (not b<90)")
        cmd.set("cartoon_transparency", 0.15, f"{t} and chain A")
        cmd.set_color("atp_col", [0.62, 0.11, 0.74])           # #9E1CBD, outside the pLDDT palette
        cmd.show("sticks", f"{t} and resn ATP"); cmd.color("atp_col", f"{t} and resn ATP")
        cmd.set_view(view)
        cmd.ray(W, H); cmd.png(f"{OUT}/B_{t}.png", dpi=300)

setup(); load_all_aligned()
view = shared_view(7)
figA(view)
figB(view)
print("PARTS DONE")
