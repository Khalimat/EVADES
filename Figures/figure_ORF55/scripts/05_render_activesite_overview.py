"""Active-site overview of ORF55 vs the Chlorella-virus DNA ligase (Fig. 3b, alternative view) - headless PyMOL.

WHAT IT DOES
    Renders the two FATCAT-superposed structures in full (ligase = grey cartoon,
    ORF55 = coral cartoon, same reference frame as the rest of Figure 3) and draws
    the 13 catalytic residues of the ligase (Nair et al. 2007) plus their
    structurally equivalent ORF55 residues as sticks. Three views (0, 90 and 180
    degree rotations about y) are ray-traced to PNG.

WHY A WHOLE-STRUCTURE VIEW
    Measuring CA-CA distances from the centroid of the 13 ligase residues on the
    FATCAT superposition shows that they do not all sit in one pocket:
      * the 8 adenylylation-motif residues (K27, D29, R32, E67, F98, E161, K186,
        K188) lie within a tight ~9 A radius - one real catalytic pocket;
      * the nick-recognition pair (R42, R176) and the three substrate/clamp-
        geometry residues (F75/C78, R285, F286) lie 11-13 A further out, on the
        DNA-gripping / clamp-closing surface.
    A single close-up therefore cannot show all 13, so the residues are shown on
    the complete aligned structures instead.

    Highlight colours differ from the parent cartoon so the residues read clearly
    against their own backbone: ORF55 residues dark red (cartoon is coral) and
    ligase residues teal (cartoon is grey).

    This is a STANDALONE figure; it is not folded into Figure3.{png,pdf,svg}.

INPUTS
    data/structures/orf55_on_2q2u_FATCAT.pdb   FATCAT superposition (chain A = ligase, chain B = ORF55)
    data/active_site_residues.tsv              residue pairs: columns ligase_resi, orf55_resi (tab-separated)
    scripts/figconfig.py                       shared colours / sizes

OUTPUT
    figures/activesite_spread/split_{1,2,3}.png

USAGE (from the figure_ORF55 directory)
    /Applications/PyMOL.app/Contents/bin/pymol -cq scripts/05_render_activesite_overview.py
"""
import csv
import os
import sys
from pymol import cmd

# Locate figconfig.py (shared colours/sizes) whether the script is launched from
# the figure root or from scripts/, and put its folder on sys.path.
for _c in (os.path.join(os.getcwd(), "scripts"),):
    if os.path.exists(os.path.join(_c, "figconfig.py")):
        sys.path.insert(0, _c)
        break
import figconfig as cfg

# Paths are all relative to the figure_ORF55 root (parent of scripts/).
ROOT   = os.path.dirname(sys.path[0])
STRUCT = os.path.join(ROOT, "data", "structures")
OUT    = os.path.join(ROOT, "figures", "activesite_spread")
os.makedirs(OUT, exist_ok=True)

# Residue-equivalence table: one row per ligase residue and its ORF55 counterpart.
with open(os.path.join(ROOT, "data", "active_site_residues.tsv")) as fh:
    PAIRS = list(csv.DictReader(fh, delimiter="\t"))

# --------------------------------------------------------------- appearance ---
cmd.bg_color(cfg.BG_COLOR)
cmd.set("ray_opaque_background", 0)
cmd.set("antialias", 2)
cmd.set("ray_trace_mode", 0)
cmd.set("ray_shadows", 0)
cmd.set("ambient", 0.40)
cmd.set("direct", 0.55)
cmd.set("specular", 0.20)
cmd.set("shininess", 13)
cmd.set("depth_cue", 0)
cmd.set("cartoon_fancy_helices", 1)
cmd.set("cartoon_flat_sheets", 1)
cmd.set("cartoon_smooth_loops", 1)
cmd.set("cartoon_transparency", 0.45)   # let the buried spheres read through
cmd.set("valence", 0)

cmd.set_color("coral", list(cfg.ORF55_COLOR))
cmd.set_color("liggrey", list(cfg.LIGASE_COLOR))
cmd.set_color("orf_hilite", [0.757, 0.153, 0.176])   # #C1272D dark red — distinct from coral cartoon
cmd.set_color("lig_hilite", [0.106, 0.482, 0.420])   # #1B7B6B teal — distinct from grey cartoon

# ------------------------------------------------------------------- build ----
cmd.load(os.path.join(STRUCT, "orf55_on_2q2u_FATCAT.pdb"), "sup")   # A=ligase B=ORF55
LIG = "sup and chain A"
ORF = "sup and chain B"

cmd.hide("everything")
cmd.show("cartoon", "sup")
cmd.color("liggrey", LIG)
cmd.color("coral", ORF)

# Select the 13 residues on each chain ("resi 27+29+32+...") and draw them as sticks.
cmd.set("stick_radius", 0.22)   # same radius as the rest of the figure (panelB insets)
resis_l = "+".join(p["ligase_resi"] for p in PAIRS)
resis_o = "+".join(p["orf55_resi"] for p in PAIRS)
lig_sel = f"({LIG}) and resi {resis_l}"
orf_sel = f"({ORF}) and resi {resis_o}"
cmd.show("sticks", f"({lig_sel}) or ({orf_sel})")
cmd.color("lig_hilite", lig_sel)
cmd.color("orf_hilite", orf_sel)

# Camera: orient on the whole complex, nudge slightly, and freeze that view so the
# three renders below are pure rotations of one common starting frame.
cmd.orient("sup")
cmd.turn("y", -15)
cmd.turn("x", 5)
cmd.zoom("sup", buffer=3, complete=1)
base_view = cmd.get_view()

# Render three views: the base view and rotations of 90 and 180 degrees about y.
for i, ty in enumerate((0, 90, 180), start=1):
    cmd.set_view(base_view)
    if ty:
        cmd.turn("y", ty)
    cmd.ray(1600, 1600)
    out = os.path.join(OUT, f"split_{i}.png")
    cmd.png(out, dpi=300)
    print("wrote", out)

print("Active-site split render done.")
