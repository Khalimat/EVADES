"""
Build the coloured AcrIC5 / PaCas8c complex (grey Cas8c, yellow PAM-binding
site, AcrIC5 coloured by real APBS electrostatic potential) and save as a
PyMOL session for interactive orientation. The camera chosen there is then pasted
into build_panel_a.py (USER_VIEW) for the final render.

INPUT: AcrIC5.cif. OUTPUT: panelA_interactive.pse.
Run: /Applications/PyMOL.app/Contents/bin/pymol -cq save_session.py
"""
import os
import sys
from pymol import cmd

# All inputs/outputs live next to this script (works with `pymol -cq <script>` from any cwd).
try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:                      # __file__ is undefined in some PyMOL launch modes
    BASE = os.getcwd()

# PyMOL bundle location (macOS default); override with the PYMOL_BIN_DIR env var.
PYMOL_BIN_DIR = os.environ.get("PYMOL_BIN_DIR", "/Applications/PyMOL.app/Contents/bin")
sys.path.insert(0, "/Applications/PyMOL.app/Contents/share/pymol/data/startup/apbs_gui")
import creating as pc          # noqa: E402
import electrostatics as pe    # noqa: E402

PAM_SITE_RESI = "205-212"  # FATCAT-confirmed correspondence to 7KHA chain I 86-92 (GVDAKGK)

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

cmd.orient("cx and chain A")
cmd.zoom("cx and chain A", buffer=5)

out_pse = os.path.join(BASE, "panelA_interactive.pse")
cmd.save(out_pse)
print("saved", out_pse)
