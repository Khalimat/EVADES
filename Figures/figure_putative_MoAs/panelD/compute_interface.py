"""
Identify AcrIIA26 (chain B) residues within 8 A of any SpyCas9 (chain A) atom,
using Bio.PDB NeighborSearch - same 8A heavy-atom-contact convention as
panelB/compute_interface.py (there: PaCas3 residues near AcrIC3; here the
roles are reversed since we want the Acr-side patch that faces Cas9).

Source model: the SpyCas9+sgRNA+AcrIIA26 AlphaFold co-fold used throughout
build_panel_d.py (seed3/model_0, ipTM 0.90 / pTM 0.86).

Run from anywhere (paths are resolved relative to this file; needs biopython):
  python3 panelD/compute_interface.py
Writes panelD/interface_residues.json, consumed by build_panel_d.py to
orient the AcrIIA26 electrostatic-surface inset toward the Cas9-contacting face.
"""
import os
import json
from Bio.PDB import MMCIFParser, NeighborSearch

# Root of figure_putative_MoAs (this script lives in its panelD/ subfolder), so it runs from any cwd.
try:
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:                      # __file__ is undefined in some PyMOL launch modes
    BASE = os.getcwd()
ACR_CIF = os.path.join(
    BASE, "panelD", "alphafold", "folds_2026_09_15_19_34",
    "spycas9_sgrna_acriia26_seed3", "fold_spycas9_sgrna_acriia26_seed3_model_0.cif",
)

# Parse the AF3 co-fold; chain A = SpyCas9, chain B = AcrIIA26.
parser = MMCIFParser(QUIET=True)
structure = parser.get_structure("cx", ACR_CIF)
model = structure[0]

chain_cas9 = model["A"]
chain_acr = model["B"]

# Index all SpyCas9 atoms; an AcrIIA26 residue is "interfacial" if ANY of its atoms
# lies within 8 A of any SpyCas9 atom.
cas9_atoms = [atom for res in chain_cas9 for atom in res]
ns = NeighborSearch(cas9_atoms)

contact_resnums = set()
for res in chain_acr:
    for atom in res:
        close = ns.search(atom.coord, 8.0)
        if close:
            contact_resnums.add(res.id[1])
            break

contact_resnums = sorted(contact_resnums)
print(f"{len(contact_resnums)} AcrIIA26 residues within 8A of SpyCas9")
print(contact_resnums)

out_path = os.path.join(BASE, "panelD", "interface_residues.json")
with open(out_path, "w") as f:
    json.dump(contact_resnums, f)
print("saved", out_path)
