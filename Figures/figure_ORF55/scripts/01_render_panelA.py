"""Panel A of Figure 3 — headless PyMOL.

Row 1 : ORF55 (coral)                     + 21-bp DNA duplex   (AlphaFold 3 model)
Row 2 : Chlorella-virus DNA ligase (grey) + product DNA        (PDB 2Q2U)

Both rows are put in one reference frame (the FATCAT superposition frame): the
AF3 ORF55-DNA model is aligned onto FATCAT chain B (ORF55) and the 2Q2U
ligase-DNA complex onto FATCAT chain A (ligase).  Each row is rendered from a
shared start view plus one 90 deg rotation about the screen x-axis (2 columns).

DNA is drawn as in the original figure: a smooth phosphodiester backbone tube
with the base pairs as sticks, coloured blue so it stands out against the salmon
protein.

INPUTS (data/structures/)
    orf55_on_2q2u_FATCAT.pdb   FATCAT superposition, used only as the reference frame
    orf55_DNA_AF3.pdb          AlphaFold 3 model of ORF55 + 21-bp DNA
    2q2u_ligase_DNA.pdb        Chlorella-virus DNA ligase-DNA complex (PDB 2Q2U)

Run:  /Applications/PyMOL.app/Contents/bin/pymol -cq scripts/01_render_panelA.py
Out:  figures/panelA/rowN_colM.png   (transparent background, square)
"""
import os
import sys
from pymol import cmd

_cands = [
    os.path.join(os.getcwd(), "scripts"),
    os.getcwd(),
]
try:
    _cands.insert(0, os.path.dirname(os.path.abspath(__file__)))
except NameError:
    pass
for _c in _cands:
    if os.path.exists(os.path.join(_c, "figconfig.py")):
        sys.path.insert(0, _c)
        break
import figconfig as cfg

ROOT   = os.path.dirname(sys.path[0]) if os.path.basename(sys.path[0]) == "scripts" else os.getcwd()
STRUCT = os.path.join(ROOT, "data", "structures")
OUT    = os.path.join(ROOT, "figures", "panelA")
os.makedirs(OUT, exist_ok=True)


# --------------------------------------------------------------- appearance ---
def scene_setup():
    """Global PyMOL look: flat lighting, no shadows, transparent ray background, and
    the cartoon/ladder settings that give the DNA its backbone-tube + rung look."""
    cmd.bg_color(cfg.BG_COLOR)
    cmd.set("ray_opaque_background", 0)
    cmd.set("antialias", 2)
    cmd.set("ray_trace_mode", 0)
    cmd.set("ray_shadows", 0)
    cmd.set("ambient", 0.36)
    cmd.set("direct", 0.55)
    cmd.set("specular", 0.20)
    cmd.set("shininess", 12)
    cmd.set("spec_count", 1)
    cmd.set("light_count", 2)
    cmd.set("depth_cue", 0)
    cmd.set("cartoon_fancy_helices", 1)
    cmd.set("cartoon_flat_sheets", 1)
    cmd.set("cartoon_smooth_loops", 1)
    cmd.set("cartoon_transparency", 0.0)
    cmd.set("cartoon_loop_radius", 0.30)
    # DNA: smooth backbone tube + one clean rung per base as sticks — the look of
    # the original figure (no base-ring detail).
    cmd.set("cartoon_ring_mode", 0)
    cmd.set("cartoon_ladder_mode", 1)
    cmd.set("cartoon_ladder_radius", 0.34)
    cmd.set("cartoon_nucleic_acid_mode", 4)
    cmd.set("cartoon_tube_radius", 0.45)


def colour_protein(sel, rgb, name):
    """Colour only the protein atoms of `sel` with a named custom RGB colour."""
    cmd.set_color(name, list(rgb))
    cmd.color(name, f"({sel}) and polymer.protein")


def colour_dna(sel):
    """Draw the nucleic acid of `sel` as a blue backbone tube with lighter-blue base rungs."""
    cmd.set_color("dna_bb", list(cfg.DNA_BACKBONE))
    cmd.set_color("dna_rung", list(cfg.DNA_BASE_CARBON))
    dna = f"({sel}) and polymer.nucleic"
    cmd.hide("sticks", dna)
    cmd.show("cartoon", dna)
    cmd.color("dna_bb", dna)                           # backbone tube (blue)
    cmd.color("dna_rung", f"{dna} and not (name P+OP1+OP2+O5'+C5'+C4'+C3'+O3'+C2'+C1'+O4')")
    cmd.set("cartoon_ladder_color", "dna_rung")        # base rungs (lighter blue)


# ------------------------------------------------------------------- build ----
scene_setup()

# FATCAT superposition — used only as the common coordinate frame (not rendered)
cmd.load(os.path.join(STRUCT, "orf55_on_2q2u_FATCAT.pdb"), "fat")
cmd.create("frame_orf55", "fat and chain B")
cmd.create("frame_ligase", "fat and chain A")
cmd.delete("fat")

# Row 1 — ORF55 + DNA (AF3)
cmd.load(os.path.join(STRUCT, "orf55_DNA_AF3.pdb"), "orf55c")
cmd.align("orf55c and chain A and polymer.protein", "frame_orf55")
cmd.hide("everything", "orf55c")
cmd.show("cartoon", "orf55c")
colour_protein("orf55c", cfg.ORF55_COLOR, "coral")
colour_dna("orf55c")

# Row 2 — Chlorella-virus ligase + product DNA (PDB 2Q2U)
cmd.load(os.path.join(STRUCT, "2q2u_ligase_DNA.pdb"), "ligc")
cmd.remove("ligc and solvent")
cmd.align("ligc and chain A and polymer.protein", "frame_ligase")
cmd.hide("everything", "ligc")
cmd.show("cartoon", "ligc")
colour_protein("ligc", cfg.LIGASE_COLOR, "grey_solo")
colour_dna("ligc")

cmd.delete("frame_orf55")
cmd.delete("frame_ligase")

# ---------------------------------------------------------------- viewpoint ---
# Start from an identity rotation matrix (looking down z), then zoom to fit the
# protein of both rows so ORF55 and the ligase are drawn at the same scale.
IDENT = (1.0, 0.0, 0.0,
         0.0, 1.0, 0.0,
         0.0, 0.0, 1.0,
         0.0, 0.0, -260.0,
         0.0, 0.0, 0.0,
         120.0, 460.0, -20.0)
cmd.set_view(IDENT)
cmd.zoom("(orf55c or ligc) and polymer.protein", buffer=1.5, complete=1)
base_view = cmd.get_view()

# One row per structure: show only that object, reset to the shared start view,
# then render N_COLS columns, rotating ROT_STEP degrees between columns.
ROWS = [("row1", "orf55c"), ("row2", "ligc")]
for row_name, obj in ROWS:
    for o in ("orf55c", "ligc"):
        cmd.disable(o)
    cmd.enable(obj)
    cmd.set_view(base_view)
    for col in range(cfg.N_COLS):
        if col > 0:
            cmd.turn(cfg.ROT_AXIS, cfg.ROT_STEP)
        cmd.ray(cfg.PANEL_PX, cfg.PANEL_PX)
        out = os.path.join(OUT, f"{row_name}_col{col + 1}.png")
        cmd.png(out, dpi=300)
        print("wrote", out)

print("Panel A done.")
