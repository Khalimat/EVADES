#!/usr/bin/env bash
# Rebuild Figure 3 end to end. Run from the figure_ORF55 directory:
#     bash scripts/run_all.sh
set -euo pipefail
cd "$(dirname "$0")/.."

PYMOL="${PYMOL:-/Applications/PyMOL.app/Contents/bin/pymol}"

echo "[1/4] Panel A  (PyMOL, ~10 s)"
"$PYMOL" -cq scripts/01_render_panelA.py

echo "[2/4] Panel B active-site residues  (PyMOL, ~20 s)"
"$PYMOL" -cq scripts/02_render_panelB.py

echo "[3/4] Panel B latch residues  (PyMOL, ~25 s)"
"$PYMOL" -cq scripts/04_render_latch.py

echo "[4/4] Assemble Figure3.{png,pdf,svg}"
python3 scripts/03_assemble_figure.py

echo "done -> figures/Figure3.png / .pdf / .svg"
