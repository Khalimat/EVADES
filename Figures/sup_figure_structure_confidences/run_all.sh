#!/usr/bin/env bash
# Regenerate every panel and the assembled figure into output/.
# Needs: pymol-open-source, numpy, matplotlib, reportlab (e.g. the conda env in README) and poppler (pdftocairo).
set -euo pipefail
cd "$(dirname "$0")/scripts"
python3 targets.py
python3 select_ntase_models.py
python3 render_plddt.py
python3 render_pae.py
python3 make_legend.py
python3 build_figure.py
cd ../output
pdftocairo -svg Supplementary_Figure_pLDDT_PAE.pdf Supplementary_Figure_pLDDT_PAE.svg
pdftocairo -png -r 300 -singlefile Supplementary_Figure_pLDDT_PAE.pdf Supplementary_Figure_pLDDT_PAE
