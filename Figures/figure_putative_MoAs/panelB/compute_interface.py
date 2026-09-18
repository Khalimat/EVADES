"""
Identify PaCas3 (chain A) residues within 8 A of any AcrIC3 (chain B) atom,
using Bio.PDB NeighborSearch - as described in the methods.

INPUT: AcrIC3.cif (in the current folder; chain A = PaCas3, chain B = AcrIC3).
OUTPUT: interface_residues.json - sorted list of PaCas3 residue numbers, used by
build_domain_bar.py to mark contacts on the domain bar.
Run: python3 compute_interface.py (needs biopython).
"""
import json
from Bio.PDB import MMCIFParser, NeighborSearch

parser = MMCIFParser(QUIET=True)
structure = parser.get_structure("cx", "AcrIC3.cif")
model = structure[0]

chain_a = model["A"]
chain_b = model["B"]

# Index all AcrIC3 atoms for fast distance queries.
b_atoms = [atom for res in chain_b for atom in res]
ns = NeighborSearch(b_atoms)

# A PaCas3 residue is an interface residue if ANY of its atoms lies within 8 A of any AcrIC3 atom.
contact_resnums = set()
for res in chain_a:
    for atom in res:
        close = ns.search(atom.coord, 8.0)
        if close:
            contact_resnums.add(res.id[1])
            break

contact_resnums = sorted(contact_resnums)
print(f"{len(contact_resnums)} PaCas3 residues within 8A of AcrIC3")
print(contact_resnums)

with open("interface_residues.json", "w") as f:
    json.dump(contact_resnums, f)
