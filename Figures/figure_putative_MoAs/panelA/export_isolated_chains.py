"""
Export isolated, single-chain structures for independent alignment
verification (e.g. via a FATCAT/DALI/FoldSeek web server):
  - PaCas8c alone (AcrIC5.cif, chain A)
  - 7KHA Cas8c homolog alone (7KHA.cif, chain I)
The resulting PDBs were uploaded to the FATCAT server to obtain the alignment in
PaCas8c.7KHA.txt, which maps the 7KHA PAM-binding residues onto PaCas8c
(see build_panel_a.py).

OUTPUT: PaCas8c_only.pdb, 7KHA_chainI_only.pdb.  Run: pymol -cq export_isolated_chains.py
"""
import os
from pymol import cmd

# All inputs/outputs live next to this script (works with `pymol -cq <script>` from any cwd).
try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:                      # __file__ is undefined in some PyMOL launch modes
    BASE = os.getcwd()

cmd.load(os.path.join(BASE, "AcrIC5.cif"), "cx")
cmd.create("PaCas8c_only", "cx and chain A and polymer")
cmd.save(os.path.join(BASE, "PaCas8c_only.pdb"), "PaCas8c_only")
print("saved PaCas8c_only.pdb")

cmd.load(os.path.join(BASE, "7KHA.cif"), "ref")
cmd.create("7KHA_chainI_only", "ref and chain I and polymer")
cmd.save(os.path.join(BASE, "7KHA_chainI_only.pdb"), "7KHA_chainI_only")
print("saved 7KHA_chainI_only.pdb")

print("DONE")
