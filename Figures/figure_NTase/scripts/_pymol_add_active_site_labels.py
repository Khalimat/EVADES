"""Run against the saved active_site.pse session to add residue labels, each
placed at the same fixed distance (FIXED_R) from its own atom, in a
direction fanned out around the ligand/ion centroid (computed relative to
the CURRENT camera) purely to pick which way each label points -- not to
vary how far it sits.

Labels are derived from whatever is ACTUALLY colored active_blue right now
(not a hardcoded residue list), so they can never drift out of sync with
the coloring, however "active_site" itself got defined/redefined earlier
in the session's history.

Usage, inside the already-open session's own command line:
  run <path-to>/figure_NTase/scripts/_pymol_add_active_site_labels.py
"""
import numpy as np
from pymol import cmd

AA3TO1 = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q",
    "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
    "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
    "TYR": "Y", "VAL": "V",
}

cmd.set("label_size", 24)
cmd.set("label_color", "black")
cmd.set("label_outline_color", -1)  # no halo

active_blue_idx = cmd.get_color_index("active_blue")
collected = []
cmd.iterate("polymer.protein and name CA", "collected.append((resi, resn, color))",
            space={"collected": collected})
LABEL_RESIDUES = {int(resi): f"{AA3TO1.get(resn, '?')}{resi}"
                  for resi, resn, color in collected if color == active_blue_idx}

if not LABEL_RESIDUES:
    print("No atoms are colored active_blue -- nothing to label. "
          "(Re-run cmd.color('active_blue', 'active_site') first if needed.)")

view = cmd.get_view()
right = np.array(view[0:3])
up = np.array(view[3:6])
center = np.array(cmd.centerofmass("lig or ions"))

items = []
for resi, text in LABEL_RESIDUES.items():
    sel = f"resi {resi} and name CA"
    pos = np.array(cmd.get_atom_coords(sel))
    rel = pos - center
    x, y = float(np.dot(rel, right)), float(np.dot(rel, up))
    angle = np.arctan2(y, x)
    items.append([sel, text, angle])

FIXED_R = 3.5  # same distance (Angstrom) from the atom for every label, no fan-out

for sel, text, angle in items:
    offset = right * (np.cos(angle) * FIXED_R) + up * (np.sin(angle) * FIXED_R)
    cmd.set("label_position", tuple(offset), sel)
    cmd.label(sel, f'"{text}"')

cmd.refresh()
print(f"Added {len(items)} labels (from active_blue-colored CAs): {[t for _, t, _ in items]}")
print("If any land badly, tell me which one and which direction to nudge it.")
