#!/usr/bin/env python3
"""Per-model protein vs DNA predicted local confidence (pLDDT) across all 25 AlphaFold 3
models per substrate, with a per-seed exact permutation test (2-nt gap vs each other
substrate) matching the ipTM/pTM test in make_supplementary_tsv.py.

pLDDT is read from the B-factor column of the AlphaFold 3 model CIFs; reported as the
mean per-residue value for the protein (chain A) and for the DNA (chains C/D/E).

Run:  python3 scripts/04_plddt_quant.py
"""
import os, glob, re, collections, itertools
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "af3_results", "folds_2026_09_03_19_12")
SUBS = {"intact": "orf55_intact_duplex_atp", "nicked": "orf55_nicked_atp",
        "gap1nt": "orf55_gap1nt_atp", "gap2nt": "orf55_gap2nt_atp"}
LAB = {"intact": "intact duplex", "nicked": "nicked",
       "gap1nt": "1-nt gap", "gap2nt": "2-nt gap"}


def res_plddt(cif):
    """mean per-residue pLDDT for protein (chain A) and DNA (chains C/D/E)."""
    prot, dna = collections.OrderedDict(), collections.OrderedDict()
    for l in open(cif):
        if not l.startswith(("ATOM", "HETATM")):
            continue
        p = l.split()
        ch, b, rid = p[6], float(p[14]), p[15]
        if ch == "A":
            prot.setdefault(rid, []).append(b)
        elif ch in ("C", "D", "E"):
            dna.setdefault((ch, rid), []).append(b)
    return (np.mean([np.mean(v) for v in prot.values()]),
            np.mean([np.mean(v) for v in dna.values()]))


def perm_test(a, b):
    """exact two-sided permutation test on the difference of means."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    obs = abs(a.mean() - b.mean())
    pool = np.concatenate([a, b]); na = len(a)
    combs = list(itertools.combinations(range(len(pool)), na))
    hits = 0
    for c in combs:
        m = np.zeros(len(pool), bool); m[list(c)] = True
        if abs(pool[m].mean() - pool[~m].mean()) >= obs - 1e-12:
            hits += 1
    return obs, hits / len(combs)


perseed = collections.defaultdict(lambda: collections.defaultdict(list))
allm = collections.defaultdict(list)
for s, pref in SUBS.items():
    for cif in sorted(glob.glob(f"{RAW}/{pref}_seed*/*_model_*.cif")):
        d = os.path.basename(os.path.dirname(cif))
        m = re.search(r"_seed(\d+)(_\d+)?$", d)
        if m.group(2):                      # accidental rerun dirs (seedN_2)
            continue
        pm, dm = res_plddt(cif)
        perseed[s][int(m.group(1))].append((pm, dm))
        allm[s].append((pm, dm))

print(f"{'substrate':<14} {'n':>3}  {'protein pLDDT':>15}  {'DNA pLDDT':>15}")
for s in SUBS:
    P = np.array([x[0] for x in allm[s]]); D = np.array([x[1] for x in allm[s]])
    print(f"{LAB[s]:<14} {len(P):>3}  {P.mean():>7.1f} +/-{P.std():>4.1f}   {D.mean():>7.1f} +/-{D.std():>4.1f}")

for name, idx in (("DNA", 1), ("protein", 0)):
    print(f"\nper-seed {name} pLDDT (mean of 5 models per seed):")
    for s in SUBS:
        v = [np.mean([x[idx] for x in perseed[s][k]]) for k in sorted(perseed[s])]
        print(f"  {LAB[s]:<14} " + "  ".join(f"{x:5.1f}" for x in v))
    print(f"exact permutation test on per-seed mean {name} pLDDT (n = 5 seeds/group):")
    g2 = [np.mean([x[idx] for x in perseed['gap2nt'][k]]) for k in sorted(perseed['gap2nt'])]
    for s in ("intact", "nicked", "gap1nt"):
        gs = [np.mean([x[idx] for x in perseed[s][k]]) for k in sorted(perseed[s])]
        obs, p = perm_test(g2, gs)
        print(f"  2-nt gap vs {LAB[s]:<13}  delta = {obs:4.1f}  P = {p:.4f}")
