import argparse
import sys
import os
import numpy as np
import pandas as pd
from collections import defaultdict

parser = argparse.ArgumentParser(description='Calculate a predicted DockQ score for a predicted structure.')
parser.add_argument('--pdbfile', nargs=1, type=str, default=sys.stdin,
                    help='Path to AlphaFold3 .cif file to be scored. Must contain at least two chains. '
                         'The B-factor column is assumed to contain the plDDT score.')

##################### FUNCTIONS #########################

def read_cif(cif_path):
    """Parse AlphaFold3 mmCIF file to extract CA/CB coordinates and plDDT scores."""
    chain_coords = {}
    chain_plddt = {}

    with open(cif_path, 'r') as f:
        lines = f.readlines()

    # Find the start of the _atom_site loop
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("_atom_site.group_PDB"):
            start_idx = i
            break
    if start_idx is None:
        raise ValueError("No _atom_site section found in CIF file.")

    # Determine where headers end and data begins
    data_start = start_idx
    while lines[data_start].strip().startswith("_"):
        data_start += 1

    # Identify column indices
    headers = lines[start_idx:data_start]
    header_map = {name.strip(): idx for idx, name in enumerate(headers)}
    
    required_fields = [
        "_atom_site.label_atom_id", "_atom_site.label_comp_id",
        "_atom_site.label_asym_id", "_atom_site.Cartn_x",
        "_atom_site.Cartn_y", "_atom_site.Cartn_z", "_atom_site.B_iso_or_equiv"
    ]
    for field in required_fields:
        if field not in header_map:
            raise ValueError(f"Missing required CIF field: {field}")

    # Parse atom lines
    for line in lines[data_start:]:
        if not line.strip() or not line.startswith("ATOM"):
            continue
        parts = line.strip().split()

        try:
            atom_name = parts[header_map["_atom_site.label_atom_id"]]
            res_name = parts[header_map["_atom_site.label_comp_id"]]
            chain = parts[header_map["_atom_site.label_asym_id"]]
            x = float(parts[header_map["_atom_site.Cartn_x"]])
            y = float(parts[header_map["_atom_site.Cartn_y"]])
            z = float(parts[header_map["_atom_site.Cartn_z"]])
            b = float(parts[header_map["_atom_site.B_iso_or_equiv"]])
        except (IndexError, ValueError):
            continue  # Skip malformed lines

        if atom_name == "CB" or (atom_name == "CA" and res_name == "GLY"):
            if chain not in chain_coords:
                chain_coords[chain] = []
                chain_plddt[chain] = []
            chain_coords[chain].append([x, y, z])
            chain_plddt[chain].append(b)

    # Convert lists to numpy arrays
    for chain in chain_coords:
        chain_coords[chain] = np.array(chain_coords[chain])
        chain_plddt[chain] = np.array(chain_plddt[chain])

    return chain_coords, chain_plddt


def calc_pdockq(chain_coords, chain_plddt, t):
    """Calculate the pDockQ scores."""
    ch1, ch2 = [*chain_coords.keys()]
    coords1, coords2 = chain_coords[ch1], chain_coords[ch2]
    plddt1, plddt2 = chain_plddt[ch1], chain_plddt[ch2]

    # Calculate pairwise distances
    mat = np.append(coords1, coords2, axis=0)
    a_min_b = mat[:, np.newaxis, :] - mat[np.newaxis, :, :]
    dists = np.sqrt(np.sum(a_min_b.T ** 2, axis=0)).T
    l1 = len(coords1)
    contact_dists = dists[:l1, l1:]
    contacts = np.argwhere(contact_dists <= t)

    if contacts.shape[0] < 1:
        pdockq = 0
        ppv = 0
    else:
        avg_if_plddt = np.average(np.concatenate([
            plddt1[np.unique(contacts[:, 0])],
            plddt2[np.unique(contacts[:, 1])]
        ]))
        n_if_contacts = contacts.shape[0]
        x = avg_if_plddt * np.log10(n_if_contacts)
        pdockq = 0.724 / (1 + np.exp(-0.052 * (x - 152.611))) + 0.018

        PPV = np.array([
            0.98128027, 0.96322524, 0.95333044, 0.9400192,
            0.93172991, 0.92420274, 0.91629946, 0.90952562, 0.90043139,
            0.8919553, 0.88570037, 0.87822061, 0.87116417, 0.86040801,
            0.85453785, 0.84294946, 0.83367787, 0.82238224, 0.81190228,
            0.80223507, 0.78549007, 0.77766077, 0.75941223, 0.74006263,
            0.73044282, 0.71391784, 0.70615739, 0.68635536, 0.66728511,
            0.63555449, 0.55890174
        ])
        pdockq_thresholds = np.array([
            0.67333079, 0.65666073, 0.63254566, 0.62604391,
            0.60150931, 0.58313803, 0.5647381, 0.54122438, 0.52314392,
            0.49659878, 0.4774676, 0.44661346, 0.42628389, 0.39990988,
            0.38479715, 0.3649393, 0.34526004, 0.3262589, 0.31475668,
            0.29750023, 0.26673725, 0.24561247, 0.21882689, 0.19651314,
            0.17606258, 0.15398168, 0.13927677, 0.12024131, 0.09996019,
            0.06968505, 0.02946438
        ])
        inds = np.argwhere(pdockq_thresholds >= pdockq)
        if len(inds) > 0:
            ppv = PPV[inds[-1]][0]
        else:
            ppv = PPV[0]

    return pdockq, ppv


################# MAIN ####################

# Parse args
args = parser.parse_args()

# Read chain coordinates and plDDT from CIF
chain_coords, chain_plddt = read_cif(args.pdbfile[0])

# Check that there are at least two chains
if len(chain_coords.keys()) < 2:
    print('Only one chain in file', args.pdbfile[0])
    sys.exit()

# Calculate pDockQ
t = 8  # Distance threshold in Å
pdockq, ppv = calc_pdockq(chain_coords, chain_plddt, t)

print('pDockQ =', np.round(pdockq, 3), 'for', args.pdbfile[0])
print('This corresponds to a PPV of at least', ppv)

