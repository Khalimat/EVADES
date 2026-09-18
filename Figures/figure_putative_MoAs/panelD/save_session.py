"""
Build the aligned, coloured Panel D complex (same as build_panel_d.py) and save
it as a PyMOL session (.pse) so it can be opened in the interactive GUI for
manual re-orientation. The camera chosen there is pasted into build_panel_d.py
(USER_VIEW) for the final renders.

OUTPUT: a .pse session in panelD/. Needs the same AlphaFold inputs as build_panel_d.py.

Two complexes sharing SpyCas9 + sgRNA, differing only in the third component:
  - SpyCas9 + sgRNA + target DNA   (native, DNA-bound state)
  - SpyCas9 + sgRNA + AcrIIA26     (target DNA replaced by AcrIIA26)
The sgRNA and AcrIIA26 shown come from the SAME co-fold (native pairing); only
the target DNA chain is imported (aligned via shared SpyCas9) from the other
complex for the overlay comparison.
"""
import os
import sys

from pymol import cmd

# Root of figure_putative_MoAs (this script lives in its panelD/ subfolder), so it runs from any cwd.
try:
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:                      # __file__ is undefined in some PyMOL launch modes
    BASE = os.getcwd()
AF_DIR = os.path.join(BASE, "panelD", "alphafold", "folds_2026_09_15_19_34")
OUT_DIR = os.path.join(BASE, "panelD")

# SpyCas9 + sgRNA + AcrIIA26 (chain A = SpyCas9, B = AcrIIA26, C = sgRNA); seed3/model_0 = best (ipTM 0.90, pTM 0.86)
ACR_CIF = os.path.join(AF_DIR, "spycas9_sgrna_acriia26_seed3", "fold_spycas9_sgrna_acriia26_seed3_model_0.cif")
# SpyCas9 + sgRNA + target DNA (chain A = SpyCas9, B = target DNA, C = sgRNA); all 4 seeds tied (ipTM 0.94, pTM 0.92)
RNADNA_CIF = os.path.join(AF_DIR, "spycas9_sgrna_targetdna_seed1", "fold_spycas9_sgrna_targetdna_seed1_model_0.cif")

# the original published AcrIIA26.cif defines the coordinate frame the main
# render script's USER_VIEW is calibrated against
REF_FRAME_CIF = os.path.join(BASE, "panelD", "AcrIIA26.cif")

# PyMOL bundle location (macOS default); override with the PYMOL_BIN_DIR env var.
PYMOL_BIN_DIR = os.environ.get("PYMOL_BIN_DIR", "/Applications/PyMOL.app/Contents/bin")
sys.path.insert(0, "/Applications/PyMOL.app/Contents/share/pymol/data/startup/apbs_gui")
import creating as pc          # noqa: E402
import electrostatics as pe    # noqa: E402

# ---------------------------------------------------------------------------
# 1. Load the two 3-chain complexes and align them on the shared SpyCas9 chain (A)
# ---------------------------------------------------------------------------
cmd.load(ACR_CIF, "cas9_acr_sgrna")     # A = SpyCas9, B = AcrIIA26, C = sgRNA
cmd.load(RNADNA_CIF, "cas9_dna_sgrna")  # A = SpyCas9, B = target DNA, C = sgRNA (own copy, unused)

cmd.align("cas9_dna_sgrna and chain A", "cas9_acr_sgrna and chain A")

# avoid chain-id collision (both objects have chain B/C) before merging; we only need chain B (target DNA)
cmd.alter("cas9_dna_sgrna and chain B", 'chain="D"')
cmd.sort()

cmd.create("complex", "cas9_acr_sgrna or (cas9_dna_sgrna and chain D)")
cmd.delete("cas9_acr_sgrna")
cmd.delete("cas9_dna_sgrna")

# final chain map in 'complex': A = SpyCas9, B = AcrIIA26, C = sgRNA, D = target DNA
cmd.set_name("complex", "cx")

# re-align onto the original AcrIIA26.cif's SpyCas9 frame so the render
# script's calibrated USER_VIEW (captured relative to that frame) still applies
cmd.load(REF_FRAME_CIF, "ref_frame")
cmd.align("cx and chain A", "ref_frame and chain A")
cmd.delete("ref_frame")

# ---------------------------------------------------------------------------
# 2. Base styling (same scheme as build_panel_d.py)
# ---------------------------------------------------------------------------
cmd.hide("everything", "cx")
cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)
cmd.set("antialias", 2)
cmd.set("cartoon_fancy_helices", 1)
cmd.set("ray_trace_mode", 0)
cmd.set("specular", 0.15)

COLOR_CAS9 = "grey70"
COLOR_ACR26 = "yellow"

cmd.show("cartoon", "cx and chain A+B+C+D")
cmd.color(COLOR_CAS9, "cx and chain A")
cmd.color(COLOR_ACR26, "cx and chain B")

# Nucleic acids: smooth backbone tube + ladder rungs (cartoon_ladder_mode),
# NOT ring/wedge cartoon and NOT raw sticks.
BACKBONE_ATOMS = "name P+OP1+OP2+O5'+C5'+C4'+C3'+O3'+C2'+C1'+O4'"

cmd.set("cartoon_ring_mode", 0)
cmd.set("cartoon_ladder_mode", 1)
cmd.set("cartoon_ladder_radius", 0.34)
cmd.set("cartoon_nucleic_acid_mode", 4)
cmd.set("cartoon_tube_radius", 0.45)

cmd.set_color("rna_bb", [0.129, 0.373, 0.125])    # forest (backbone tube)
cmd.set_color("rna_rung", [0.55, 0.80, 0.55])     # lighter green (base rungs)
cmd.color("rna_bb", "cx and chain C")
cmd.color("rna_rung", f"cx and chain C and not ({BACKBONE_ATOMS})")
cmd.set("cartoon_ladder_color", "rna_rung", "cx and chain C")

cmd.set_color("dna_bb", [0.95, 0.45, 0.0])        # vivid orange (backbone tube)
cmd.set_color("dna_rung", [1.0, 0.70, 0.30])      # lighter orange (base rungs)
cmd.color("dna_bb", "cx and chain D")
cmd.color("dna_rung", f"cx and chain D and not ({BACKBONE_ATOMS})")
cmd.set("cartoon_ladder_color", "dna_rung", "cx and chain D")

cmd.hide("cartoon", "cx and chain D")  # toggle on with: show cartoon, cx and chain D

# ---------------------------------------------------------------------------
# 3. Real APBS electrostatic potential on AcrIIA26 (chain B) -> object 'acr_pqr'
# ---------------------------------------------------------------------------
warnings = pc.pdb2pqr_cli(
    "acr_pqr", "cx and chain B", options=["--ff=amber"], state=1, quiet=0,
    exe=os.path.join(PYMOL_BIN_DIR, "pdb2pqr"),
)
if warnings:
    print("pdb2pqr warnings:", warnings)

pe.map_new_apbs(
    "acr_map", "acr_pqr", grid=0.5, buffer=10.0, quiet=0,
    exe=os.path.join(PYMOL_BIN_DIR, "apbs"),
)

cmd.ramp_new("acr_ramp", "acr_map", [-5, 0, 5], color=["red", "white", "blue"])
cmd.set("surface_ramp_above_mode", 1, "acr_pqr")
cmd.set("surface_solvent", 0, "acr_pqr")
cmd.set("surface_quality", 1, "acr_pqr")
cmd.set("surface_color", "acr_ramp", "acr_pqr")
cmd.hide("everything", "acr_pqr")  # off by default; enable + `show surface, acr_pqr` to see it
cmd.disable("acr_pqr")
cmd.disable("acr_ramp")
cmd.disable("acr_map")

# ---------------------------------------------------------------------------
# 4. Starting camera (adjust freely in the GUI)
# ---------------------------------------------------------------------------
cmd.orient("cx and chain A")
cmd.zoom("cx and chain A", buffer=5)

out_pse = os.path.join(OUT_DIR, "panelD_interactive.pse")
cmd.save(out_pse)
print("saved", out_pse)
