#!/usr/bin/env python3
"""Open the Panel D active-site scene in the interactive PyMOL GUI, for
manual inspection/tweaking (labels, camera, etc.) -- see _pymol_open_active_site.py
for how to feed changes back into build_panel_d.py.

Run: python3 scripts/open_active_site_pymol.py
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_panel_d import find_best_model, find_pymol, SUPERPOSED_PDB, VIEW_JSON  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "scripts")


def main():
    if not os.path.isfile(SUPERPOSED_PDB):
        sys.exit(f"Missing pre-superposed structure at {SUPERPOSED_PDB}")
    if not os.path.isfile(VIEW_JSON):
        sys.exit(f"Missing {VIEW_JSON} -- run build_panel_a.py first.")

    score, cif_path = find_best_model()
    print(f"Opening {cif_path} (ranking_score={score:.3f}) in PyMOL...")

    pymol = find_pymol()
    subprocess.Popen(
        [pymol, os.path.join(SCRIPTS, "_pymol_open_active_site.py"),
         "--", cif_path, SUPERPOSED_PDB, VIEW_JSON],
    )
    print("PyMOL launched in the background -- switch to its window.")


if __name__ == "__main__":
    main()
