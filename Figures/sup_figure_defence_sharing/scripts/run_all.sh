#!/bin/bash
# Rebuild Defence_sharing_figure.svg / .png. Run from the project root:  bash scripts/run_all.sh
# Needs: PyMOL (app), Google Chrome (PNG export), and a Python with pandas, networkx, matplotlib, pillow.
PYMOL=/Applications/PyMOL.app/Contents/MacOS/PyMOL
PY=${PY:-python3}
$PY scripts/01_make_network_svg.py                # panel A  -> panels/panelA_network.svg
$PYMOL -cq scripts/02_align_drmMI_view.py         # views    -> sessions/drmMI_aligned.pse   (gp28 view: sessions/gp28_oriented.pse, set by hand)
$PYMOL -cq scripts/03_render_complex_surface.py   # panel B  -> panels/panelB_*_complex.png  (ray tracing, a few minutes)
$PY scripts/04_make_figure.py                     # merge    -> Defence_sharing_figure.svg / .png
