"""Build AlphaFold Server job JSONs (one seed) from the sequences in the published models,
so the same complexes could be re-run to obtain PAE matrices. Writes inputs/af3_server_jobs/."""
import json, os
from targets import ROOT

SRC = os.path.join(ROOT, "inputs", "published_models")
OUT = os.path.join(ROOT, "inputs", "af3_server_jobs")
os.makedirs(OUT, exist_ok=True)

aa3to1 = {
 'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I',
 'LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V',
}

targets = {
    "AcrIB4":        "AcrIB4.cif",
    "AcrIC3":        "AcrIC3.cif",
    "AcrIC5":        "AcrIC5.cif",
    "AcrIIA26":      "AcrIIA26.cif",
    "DISARM_Ocr_complex":   "ocr_disarm_2_disarm_2_drmmii_0_v_data_model.cif",
    "Panchino_Ocr_complex": "ocr_panchino_gp28_gp28_data_model.cif",
}

def extract_sequences(path):
    seqs, order, in_block = {}, [], False
    with open(path) as f:
        for line in f:
            if line.startswith('_entity_poly_seq.'):
                in_block = True
                continue
            if in_block:
                if line.startswith('#'):
                    break
                parts = line.split()
                if len(parts) >= 4:
                    ent, mon = parts[0], parts[2]
                    if ent not in seqs:
                        seqs[ent] = []
                        order.append(ent)
                    seqs[ent].append(aa3to1.get(mon, 'X'))
    return [''.join(seqs[e]) for e in order]

for name, fn in targets.items():
    seqs = extract_sequences(os.path.join(SRC, fn))
    job = [{
        "name": f"{name}_reseed_for_PAE_seed1",
        "modelSeeds": [1],
        "sequences": [{"proteinChain": {"sequence": s, "count": 1}} for s in seqs],
    }]
    out_path = os.path.join(OUT, f"afserver_{name}.json")
    with open(out_path, "w") as f:
        json.dump(job, f, indent=2)
    print(f"wrote {out_path}  chain lengths {[len(s) for s in seqs]}")
