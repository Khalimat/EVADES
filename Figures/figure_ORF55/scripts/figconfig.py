"""Shared constants for the ORF55 / Chlorella-virus DNA-ligase figure.

Imported by the PyMOL render scripts (01, 02) and the montage script (03).
Keeping every colour / view / size in one place is what makes the three
Panel-A rows and the Panel-B insets look like one figure.
"""

# ---------------------------------------------------------------- palette ----
# ORF55 (DruSM1 phage)  -> warm coral   |  Chlorella-virus DNA ligase -> grey
ORF55_COLOR      = (0.918, 0.533, 0.482)   # #EA887B
LIGASE_COLOR     = (0.505, 0.505, 0.505)   # #818181
LIGASE_COLOR_SUP = (0.620, 0.620, 0.620)   # slightly lighter grey for the overlay row

# DNA  -> a cool blue, so it reads clearly against the salmon protein (and grey)
DNA_BACKBONE     = (0.145, 0.470, 0.740)   # #2578BD  phosphodiester backbone tube
DNA_BASE_CARBON  = (0.420, 0.660, 0.850)   # #6BA8D9  base rungs (lighter blue)

# active-site sticks (Panel B) reuse ORF55_COLOR / LIGASE_COLOR for carbons

BG_COLOR = "white"

# ---------------------------------------------------------------- geometry ---
# Panel A: N_COLS columns = the start view + successive 90 deg rotations about
# the screen x-axis.  N_COLS = 2  ->  one rotation only.
N_COLS      = 2
ROT_AXIS    = "x"
ROT_STEP    = 90.0

# Per-panel raytraced size (square).  Montage downsamples.
PANEL_PX    = 1200
INSET_PX    = 900

# ray/quality
RAY_SAMPLES = 8
