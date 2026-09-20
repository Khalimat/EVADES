#!/usr/bin/env bash
# Regenerate the figure from the raw AlphaFold 3 models. Run from anywhere.
# Needs: python3 with numpy + pillow; PyMOL (set PYMOL=/path/to/pymol if not on PATH).
set -euo pipefail
cd "$(dirname "$0")"
PYMOL="${PYMOL:-$(command -v pymol || echo /Applications/PyMOL.app/Contents/bin/pymol)}"

python3 scripts/01_select_models.py                 # raw AF3 output -> models/
FIG_ROOT="$PWD" "$PYMOL" -cq scripts/02_pymol_render.py             # models/ -> output/parts/{A,B}_<substrate>.png
python3 scripts/03_montage.py                       # panels -> output/SuppFig_*.png + caption
python3 scripts/04_plddt_quant.py | tee output/plddt_stats.txt   # numbers quoted in the caption
