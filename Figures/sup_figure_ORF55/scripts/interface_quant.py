"""Quantify the ORF55-DNA interface, controlling for DNA length.
Run: /Applications/PyMOL.app/Contents/bin/pymol -cq scripts/interface_quant.py
Top-ranked model per seed (models/<sub>_seed<1-5>.cif); seed = replicate (n=5).
Produces Supplementary Table (interface quantification) + legend referenced by
the Supplementary Figure caption ("the buried surface area and the number of
protein-DNA hydrogen bonds per nucleotide are the same for all four substrates,
and contacts to the constant-length template strand do not fall with gap size")."""
import os, glob
import numpy as np
from pymol import cmd

REPO = "/Users/khali/Desktop/EVADES/Figures/sup_figure_ORF55"
M = os.path.join(REPO, "models")
OUT = os.path.join(REPO, "supplementary")
os.makedirs(OUT, exist_ok=True)
SUBS = ["intact", "nicked", "gap1nt", "gap2nt"]
LAB  = {"intact": "intact duplex", "nicked": "nicked", "gap1nt": "1-nt gap", "gap2nt": "2-nt gap"}

def area(sel):
    return cmd.get_area(sel)

def bsa(complex_obj, sel_a, sel_b):
    """buried SASA between two chain groups of a loaded complex object"""
    cmd.create("_a", f"{complex_obj} and ({sel_a})")
    cmd.create("_b", f"{complex_obj} and ({sel_b})")
    cmd.flag("ignore", "_a or _b", "clear")
    free = area("_a") + area("_b")
    bound = area(f"{complex_obj} and ({sel_a})") + area(f"{complex_obj} and ({sel_b})")
    cmd.delete("_a _b")
    return (free - bound) / 2.0

def hb(obj, protsel, dnasel):
    prs = cmd.find_pairs(f"{obj} and ({protsel}) and (elem N+O) and not name N",
                         f"{obj} and ({dnasel}) and (elem N+O)", cutoff=3.5, mode=0)
    return len(prs)

def n_nt(obj, chains):
    return cmd.count_atoms(f"{obj} and chain {chains} and name C1'")

rows = {s: [] for s in SUBS}
for s in SUBS:
    for f in sorted(glob.glob(f"{M}/{s}_seed*.cif")):
        cmd.reinitialize()
        cmd.set("dot_solvent", 1); cmd.set("dot_density", 3)
        cmd.load(f, "m")
        cmd.flag("ignore", "none", "clear")
        chs = cmd.get_chains("m")
        dna = "+".join(c for c in chs if c in ("C", "D", "E"))
        n_all, n_C = n_nt("m", dna), n_nt("m", "C")
        b_tot = bsa("m", "chain A", f"chain {dna}")
        b_tmpl = bsa("m", "chain A", "chain C")
        h_tot = hb("m", "chain A", f"chain {dna}")
        h_tmpl = hb("m", "chain A", "chain C")
        ifr = len({a.resi for a in cmd.get_model(
            f"byres (m and chain A within 4 of (m and chain {dna}))").atom if a.name == "CA"})
        rows[s].append(dict(bsa_tot=b_tot, bsa_tmpl=b_tmpl, bsa_per_nt=b_tot / n_all,
                            bsa_per_nt_tmpl=b_tmpl / n_C,
                            hb_tot=h_tot, hb_tmpl=h_tmpl, hb_per_nt=h_tot / n_all,
                            hb_per_nt_tmpl=h_tmpl / n_C, ifres=ifr, n_dna=n_all))

keys = [("bsa_tot", "buried SASA, total (A^2)"),
        ("bsa_per_nt", "buried SASA per DNA nt (A^2)"),
        ("bsa_tmpl", "buried SASA, continuous strand only (A^2)"),
        ("bsa_per_nt_tmpl", "buried SASA per continuous-strand nt (21 nt, constant)"),
        ("hb_tot", "protein-DNA H-bonds, total"),
        ("hb_per_nt", "H-bonds per DNA nt"),
        ("hb_tmpl", "H-bonds to continuous strand (21 nt, constant)"),
        ("hb_per_nt_tmpl", "H-bonds per continuous-strand nt"),
        ("ifres", "distinct interface residues"),
        ("n_dna", "DNA nucleotides in the model")]
w = max(len(l) for _, l in keys)
print(f"\n{'metric (mean +/- s.d., n=5 seeds)':<{w}} " + "".join(f"{LAB[s]:>16}" for s in SUBS))
print("-" * (w + 1 + 16 * len(SUBS)))
for k, lab in keys:
    cells = []
    for s in SUBS:
        v = np.array([r[k] for r in rows[s]], float)
        cells.append(f"{v.mean():.2f}+/-{v.std():.2f}" if v.mean() < 20 else f"{v.mean():.0f}+/-{v.std():.0f}")
    print(f"{lab:<{w}} " + "".join(f"{c:>16}" for c in cells))

out = os.path.join(OUT, "AF3_interface_quant.tsv")
with open(out, "w") as fh:
    fh.write("metric\t" + "\t".join(f"{s}_mean\t{s}_sd" for s in SUBS) + "\tn_seeds\n")
    for k, lab in keys:
        c = [lab]
        for s in SUBS:
            v = np.array([r[k] for r in rows[s]], float)
            c += [f"{v.mean():.3f}", f"{v.std():.3f}"]
        c.append("5")
        fh.write("\t".join(c) + "\n")
print(f"\nwrote {out}")
