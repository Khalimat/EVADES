"""
Recreate Figure 1, Panel D.

Colour design: no protein or nucleic acid is coloured red or blue where the panel
also shows APBS electrostatic potential (which uses a red<->blue scale), so the
sgRNA is drawn in green and the target DNA in orange. SpyCas9 is grey and
AcrIIA26 yellow; none of these co-occur with the electrostatic map.

Two complexes sharing SpyCas9 + sgRNA, differing only in the third component:
  - SpyCas9 + sgRNA + target DNA   (native, DNA-bound state)
  - SpyCas9 + sgRNA + AcrIIA26     (target DNA replaced by AcrIIA26)
The sgRNA and AcrIIA26 shown come from the SAME co-fold (native pairing); only
the target DNA chain is imported (aligned via shared SpyCas9) from the other
complex for the overlay comparison.

The isolated AcrIIA26 electrostatic-surface inset (bottom-right / "04") is
given a DELIBERATE, reportable rotation instead of PyMOL's automatic `orient`
alone (which just fits principal axes and has no notion of which face
contacted Cas9):
  1. `orient` on isolated AcrIIA26 (chain B) alone - principal-axis best fit.
  2. Using the AcrIIA26 residues within 8A of any SpyCas9 atom (computed in
     compute_interface.py, same 8A heavy-atom convention as
     panelB/compute_interface.py), take the centroid of the actual contacting
     atoms vs. the centroid of the whole chain -> outward vector for the
     Cas9-facing patch.
  3. If that vector points away from the camera after step 1, apply a single
     180 degree turn about the vertical (screen y) axis so the Cas9-contacting
     face points toward the viewer. (If it already points at the viewer, no
     flip is needed - recorded either way.)
This makes the inset's orientation a specific, citable transform rather than
an arbitrary PCA fit - see rotation_report.json.

INPUTS
  panelD/alphafold/folds_*/...   AlphaFold 3 co-folds (SpyCas9+sgRNA+AcrIIA26, SpyCas9+sgRNA+target DNA);
                                 large raw outputs, not tracked in git - regenerate with Analysis/run_alphafold3
  panelD/AcrIIA26.cif            reference frame the saved camera was calibrated against
  panelD/interface_residues.json from compute_interface.py
OUTPUTS (panelD/)
  01_overview_cas9_acr26_sgrna.png, 02_overview_with_targetDNA.png,
  03_electrostatic_overview.png, 04_electrostatic_zoom.png, rotation_report.json
  (then run compose_panel_d.py)

Run headlessly with the PyMOL bundle that ships pdb2pqr + apbs:
  /Applications/PyMOL.app/Contents/bin/pymol -cq panelD/build_panel_d.py
"""
import os
import sys
import json

import numpy as np
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

# the original AcrIIA26.cif defines the coordinate frame the saved camera view
# (USER_VIEW, below) was calibrated against
REF_FRAME_CIF = os.path.join(BASE, "panelD", "AcrIIA26.cif")

# AcrIIA26 residues within 8A of SpyCas9 (from compute_interface.py)
INTERFACE_JSON = os.path.join(OUT_DIR, "interface_residues.json")

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

# re-align onto the original AcrIIA26.cif's SpyCas9 frame so the previously
# calibrated USER_VIEW camera (captured relative to that frame) still applies
cmd.load(REF_FRAME_CIF, "ref_frame")
cmd.align("cx and chain A", "ref_frame and chain A")
cmd.delete("ref_frame")

# ---------------------------------------------------------------------------
# 2. Base styling
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
# sgRNA/DNA colours are defined below via set_color (rna_bb/dna_bb): sgRNA is
# green, kept off the red/blue electrostatic scale

cmd.show("cartoon", "cx and chain A+B+C+D")
cmd.color(COLOR_CAS9, "cx and chain A")
cmd.color(COLOR_ACR26, "cx and chain B")

# Nucleic acids drawn as in figure_ORF55/scripts/01_render_panelA.py: a smooth
# backbone tube + one clean ladder rung per base pair (cartoon_ladder_mode),
# NOT the ring/wedge cartoon (ring_mode) and NOT raw all-atom sticks.
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

cmd.set_color("dna_bb", [0.95, 0.45, 0.0])        # vivid orange (backbone tube) - high visibility, off the red/blue electrostatic scale
cmd.set_color("dna_rung", [1.0, 0.70, 0.30])      # lighter orange (base rungs)
cmd.color("dna_bb", "cx and chain D")
cmd.color("dna_rung", f"cx and chain D and not ({BACKBONE_ATOMS})")
cmd.set("cartoon_ladder_color", "dna_rung", "cx and chain D")

cmd.hide("cartoon", "cx and chain D")

USER_VIEW = (
    -0.5105695128440857, 0.24553121626377106, -0.824033796787262,
    -0.5530683398246765, 0.6400192975997925, 0.5333791375160217,
    0.6583587527275085, 0.7280731797218323, -0.1909787356853485,
    0.0, 0.0, -429.9999694824219,
    1.4330215454101562, -0.4526023864746094, 3.0344085693359375,
    315.64697265625, 544.3530883789062, -20.0,
)

def set_main_view():
    """Restore the shared camera (rotation, position and full clip slab) used for the complex panels."""
    # camera saved after orienting the scene interactively in PyMOL
    cmd.set_view(USER_VIEW)

set_main_view()

def shot(name, width=1800, height=1400):
    """Ray-trace the current scene to OUT_DIR/`name` (PNG, 300 dpi)."""
    cmd.ray(width, height)
    cmd.png(os.path.join(OUT_DIR, name), dpi=300)
    print("saved", name)

# ---------------------------------------------------------------------------
# Panel D top-left: overview (SpyCas9 + AcrIIA26 + sgRNA), no DNA
# ---------------------------------------------------------------------------
shot("01_overview_cas9_acr26_sgrna.png")

# ---------------------------------------------------------------------------
# Panel D bottom-left: the OTHER complex - SpyCas9 + sgRNA + target DNA,
# WITHOUT AcrIIA26 (target DNA is not present together with AcrIIA26; they are
# alternate third components of two separate co-folds, not shown cumulatively)
# ---------------------------------------------------------------------------
cmd.hide("cartoon", "cx and chain B")   # remove AcrIIA26
cmd.show("cartoon", "cx and chain D")   # target DNA: backbone tube + ladder rungs (set up above)
# narrow clip slab (near/far) chosen interactively in PyMOL (Clip mouse action,
# not fog/transparency): same slab centre as USER_VIEW (430.0) but narrowed from
# width 228.7 to 54.15, so only a thin slice of the
# complex around the sgRNA/DNA channel is drawn and the rest is clipped away.
cmd.clip("slab", 54.145721435546875)
shot("02_overview_with_targetDNA.png")
set_main_view()  # restore the full (unclipped) slab for subsequent panels
cmd.hide("cartoon", "cx and chain D")   # revert for subsequent panels
cmd.hide("sticks", "cx and chain D")
cmd.show("cartoon", "cx and chain B")   # restore AcrIIA26

# ---------------------------------------------------------------------------
# 3. Real APBS electrostatic potential on AcrIIA26 (chain B)
# ---------------------------------------------------------------------------
warnings = pc.pdb2pqr_cli(
    "acr_pqr",
    "cx and chain B",
    options=["--ff=amber"],
    state=1,
    quiet=0,
    exe=os.path.join(PYMOL_BIN_DIR, "pdb2pqr"),
)
if warnings:
    print("pdb2pqr warnings:", warnings)

pe.map_new_apbs(
    "acr_map",
    "acr_pqr",
    grid=0.5,
    buffer=10.0,
    quiet=0,
    exe=os.path.join(PYMOL_BIN_DIR, "apbs"),
)

cmd.ramp_new("acr_ramp", "acr_map", [-5, 0, 5], color=["red", "white", "blue"])
cmd.set("surface_ramp_above_mode", 1, "acr_pqr")
cmd.set("surface_solvent", 0, "acr_pqr")
cmd.set("surface_quality", 1, "acr_pqr")
cmd.set("surface_color", "acr_ramp", "acr_pqr")
cmd.show("surface", "acr_pqr")
cmd.hide("cartoon", "cx and chain B")
cmd.disable("acr_ramp")  # keep the colouring, hide PyMOL's own legend bar; we draw one shared bar in compositing

# ---------------------------------------------------------------------------
# Panel D top-right: SpyCas9 + sgRNA (green) + AcrIIA26 electrostatic surface
# ---------------------------------------------------------------------------
set_main_view()
shot("03_electrostatic_overview.png")

# ---------------------------------------------------------------------------
# Panel D zoom inset (bottom-right): AcrIIA26 electrostatic surface only,
# deliberately rotated to face the SpyCas9-contacting side toward the viewer
# (see module docstring; full numeric trail in rotation_report.json)
# ---------------------------------------------------------------------------
with open(INTERFACE_JSON) as f:
    interface_resnums = json.load(f)
resi_sel = "+".join(str(r) for r in interface_resnums)

cmd.disable("cx")
cmd.orient("acr_pqr")           # baseline: principal-axis best fit, isolated
cmd.zoom("acr_pqr", buffer=2)

view_after_orient = cmd.get_view()
R = np.array(view_after_orient[0:9]).reshape(3, 3)

whole_com = cmd.centerofmass("acr_pqr")
# acr_pqr is a fresh pdb2pqr object (renumbered/reprotonated) but shares the
# same heavy-atom coordinates as cx/chain B, so selecting by resi here
# identifies the same spatial patch computed in compute_interface.py
contact_com = cmd.centerofmass(f"acr_pqr and resi {resi_sel}")

v = np.array(contact_com) - np.array(whole_com)
v = v / np.linalg.norm(v)
camera_vec = R @ v  # displacement of the interface patch in camera axes

flipped = bool(camera_vec[2] < 0)
if flipped:
    cmd.turn("y", 180)
    cmd.zoom("acr_pqr", buffer=2)

view_final = cmd.get_view()

# no clip/fog here: the narrow-slab treatment is only for the complex (row 2
# left), not this isolated AcrIIA26-alone inset
shot("04_electrostatic_zoom.png")
cmd.enable("cx")

# ---------------------------------------------------------------------------
# Report the exact transition from the complex view (USER_VIEW) to this
# inset, for the methods/figure legend text.
# ---------------------------------------------------------------------------
Ra = np.array(USER_VIEW[0:9]).reshape(3, 3)
Rb = np.array(view_final[0:9]).reshape(3, 3)
Rrel = Rb @ Ra.T
angle = float(np.degrees(np.arccos(np.clip((np.trace(Rrel) - 1) / 2, -1, 1))))
axis = np.array([
    Rrel[2, 1] - Rrel[1, 2],
    Rrel[0, 2] - Rrel[2, 0],
    Rrel[1, 0] - Rrel[0, 1],
])
norm = np.linalg.norm(axis)
axis = (axis / norm).tolist() if norm > 1e-8 else [0.0, 0.0, 0.0]

report = {
    "interface_definition": "AcrIIA26 (chain B) residues with any atom within 8A of any SpyCas9 (chain A) atom",
    "n_interface_residues": len(interface_resnums),
    "interface_residues": interface_resnums,
    "orient_then_flip_180_about_y": flipped,
    "camera_vec_after_orient": camera_vec.tolist(),
    "relative_rotation_vs_complex_view__angle_deg": angle,
    "relative_rotation_vs_complex_view__axis_screen_frame_xyz": axis,
    "note": (
        "axis/angle above are relative to USER_VIEW (the complex view, Fig 1D "
        "top-right, panel 03); axis is expressed in that view's own screen "
        "frame (x=right, y=up, z=toward viewer)."
    ),
}
with open(os.path.join(OUT_DIR, "rotation_report.json"), "w") as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))

print("DONE")
