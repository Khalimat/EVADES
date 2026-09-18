"""
Recreate Figure 1, Panel A: AcrIC5 vs Pseudomonas aeruginosa Cas8c (PaCas8c).

Per the methods:
  - AF3 complex: PaCas8c (chain A, 597 aa, UEM35121.1) + AcrIC5 (chain B, 60 aa)
  - PAM-binding motif "GVDAKGK" is NOT a substring of PaCas8c's own sequence
    (checked against the real NCBI UEM35121.1 record). It IS present verbatim
    in the reference structure 7KHA (chain I, residues 86-92) - confirmed
    directly from Figure 2d of the paper describing 7KHA (O'Brien et al 2020,
    Nat Commun 11:5931, PMID 33230133), which labels G86-V87-D88-A89-K90-G91-
    K92 as "Putative PAM site residues".
  - Transferred to PaCas8c via a real FATCAT 2.0 alignment (run at
    the FATCAT web server; PaCas8c.7KHA.txt), not just PyMOL cealign - giving
    an exact 1:1 residue correspondence: G86->G205, V87->A206, D88->Q207,
    A89->S208, (S209 inserted, unaligned), K90->G210, G91->A211, K92->S212.
    So the PAM-binding site in PaCas8c is residues 205-212 (GAQS.GAS).
  - AcrIC5 coloured by real APBS electrostatic potential (not a flat colour).

INPUTS (this folder): AcrIC5.cif (AF3 model of PaCas8c + AcrIC5), PaCas8c.7KHA.txt (FATCAT alignment).
OUTPUT: PanelA_render.png (next step: compose_panel_a.py).
Needs PyMOL with its bundled APBS / pdb2pqr.

Run: /Applications/PyMOL.app/Contents/bin/pymol -cq panelA/build_panel_a.py
"""
import os
import sys
from pymol import cmd

# All inputs/outputs live next to this script (works with `pymol -cq <script>` from any cwd).
try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:                      # __file__ is undefined in some PyMOL launch modes
    BASE = os.getcwd()
OUT_DIR = BASE

# PyMOL bundle location (macOS default); override with the PYMOL_BIN_DIR env var.
PYMOL_BIN_DIR = os.environ.get("PYMOL_BIN_DIR", "/Applications/PyMOL.app/Contents/bin")
sys.path.insert(0, "/Applications/PyMOL.app/Contents/share/pymol/data/startup/apbs_gui")
import creating as pc          # noqa: E402
import electrostatics as pe    # noqa: E402

PAM_SITE_RESI = "205-212"  # FATCAT-confirmed correspondence to 7KHA chain I 86-92 (GVDAKGK)

# Scene setup: PaCas8c as a grey cartoon with the PAM-binding stretch as yellow sticks.
cmd.load(os.path.join(BASE, "AcrIC5.cif"), "cx")
# chain A = PaCas8c (597 aa), chain B = AcrIC5 (60 aa)

cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)
cmd.set("antialias", 2)
cmd.set("cartoon_fancy_helices", 1)
cmd.set("ray_trace_mode", 0)
cmd.set("specular", 0.15)

cmd.hide("everything", "cx")
cmd.show("cartoon", "cx and chain A")
cmd.color("grey70", "cx and chain A")

cmd.select("pam_site", f"cx and chain A and resi {PAM_SITE_RESI}")
cmd.show("sticks", "pam_site")
cmd.color("yellow", "pam_site")

# ---------------------------------------------------------------------------
# Real APBS electrostatic potential on AcrIC5 (chain B)
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
cmd.show("surface", "acr_pqr")
cmd.disable("acr_ramp")

USER_VIEW = (
    0.4446243941783905, 0.8763439059257507, 0.18529127538204193,
    0.0805952399969101, -0.2451661378145218, 0.9661252498626709,
    0.8920832872390747, -0.4146290421485901, -0.17963391542434692,
    0.0, 0.0, -303.326904296875,
    1.2289276123046875, -0.35565185546875, -2.1590576171875,
    -1450.2666015625, 2056.92138671875, -20.0,
)
cmd.set_view(USER_VIEW)  # camera saved after orienting the scene interactively in PyMOL

# Ray-trace at 1600x1100 and write the PNG.
cmd.ray(1600, 1100)
cmd.png(os.path.join(OUT_DIR, "PanelA_render.png"), dpi=300)
print("saved PanelA_render.png")
print("DONE")
