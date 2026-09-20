#!/usr/bin/env python3
"""Build the TSV tables from the raw AlphaFold3 output.

Writes into ../output/ :
  AF3_perModel_results.tsv     one row per model: substrate, seed, sample, ipTM, pTM, ranking
  AF3_summary_confidence.tsv   mean +/- s.d. of ipTM / pTM / ranking per substrate

Also prints the confidence table and a significance test for the 2-nt gap.
"""
import os, re, glob, json, itertools, collections, numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(REPO, "af3_results", "folds_2026_09_03_19_12")
OUT  = os.path.join(REPO, "output"); os.makedirs(OUT, exist_ok=True)

SUBS  = ["intact_duplex", "nicked", "gap1nt", "gap2nt"]
LABEL = {"intact_duplex":"intact duplex (control)", "nicked":"nicked",
         "gap1nt":"1-nt gap", "gap2nt":"2-nt gap"}

def subseed(path):
    d = os.path.basename(os.path.dirname(path))
    return re.match(r"orf55_(intact_duplex|nicked|gap1nt|gap2nt)_atp_seed(\d+)(_\d+)?$", d)

# ============================================================ confidence
per_model = collections.defaultdict(list)          # substrate -> [dict,...]
for sc in sorted(glob.glob(f"{ROOT}/orf55_*/*_summary_confidences_*.json")):
    m = subseed(sc)
    if not m or m.group(3):                        # skip accidental intact_duplex re-runs
        continue
    j = json.load(open(sc))
    per_model[m.group(1)].append(dict(seed=int(m.group(2)),
        sample=int(re.search(r"_(\d+)\.json$", sc).group(1)),
        iptm=j["iptm"], ptm=j["ptm"], ranking=j["ranking_score"]))

with open(os.path.join(OUT, "AF3_perModel_results.tsv"), "w") as fh:
    fh.write("substrate\tsubstrate_label\tseed\tsample\tiptm\tptm\tranking_score\n")
    for s in SUBS:
        for r in sorted(per_model[s], key=lambda x:(x["seed"], x["sample"])):
            fh.write(f"{s}\t{LABEL[s]}\t{r['seed']}\t{r['sample']}\t"
                     f"{r['iptm']:.3f}\t{r['ptm']:.3f}\t{r['ranking']:.3f}\n")

def ms(x): x=np.array(x,float); return x.mean(), x.std()
with open(os.path.join(OUT, "AF3_summary_confidence.tsv"), "w") as fh:
    fh.write("substrate\tn_models\tn_seeds\tiptm_mean\tiptm_sd\tptm_mean\tptm_sd\tranking_mean\tranking_sd\n")
    for s in SUBS:
        r = per_model[s]
        im, isd = ms([x["iptm"] for x in r]); pm, psd = ms([x["ptm"] for x in r])
        rm, rsd = ms([x["ranking"] for x in r]); ns = len({x["seed"] for x in r})
        fh.write(f"{LABEL[s]}\t{len(r)}\t{ns}\t{im:.4f}\t{isd:.4f}\t{pm:.4f}\t{psd:.4f}\t{rm:.4f}\t{rsd:.4f}\n")

# significance: 2-nt gap vs the other three, exact permutation on per-seed top-ranked ipTM/pTM
def perseed_top(metric):
    out = {}
    for s in SUBS:
        byseed = collections.defaultdict(list)
        for sc in glob.glob(f"{ROOT}/orf55_{s}_atp_seed*/*_summary_confidences_*.json"):
            if subseed(sc).group(3): continue
            j = json.load(open(sc)); byseed[subseed(sc).group(2)].append(j)
        out[s] = [max(v, key=lambda z: z["ranking_score"])[metric] for v in byseed.values()]
    return out
def exact_perm(a, b):
    a, b = np.array(a,float), np.array(b,float); obs = a.mean()-b.mean()
    pool = np.concatenate([a, b]); na = len(a); dif = []
    for idx in itertools.combinations(range(len(pool)), na):
        msk = np.zeros(len(pool), bool); msk[list(idx)] = True
        dif.append(pool[msk].mean() - pool[~msk].mean())
    return obs, float(np.mean(np.array(dif) <= obs + 1e-12))

print("\n=== AF3 confidence (n = 25 models = 5 seeds x 5 samples) ===")
print(f"{'substrate':<26}{'ipTM':>16}{'pTM':>16}{'ranking':>16}")
for s in SUBS:
    r = per_model[s]
    im, isd = ms([x['iptm'] for x in r]); pm, psd = ms([x['ptm'] for x in r]); rm, rsd = ms([x['ranking'] for x in r])
    print(f"{LABEL[s]:<26}{im:8.3f} +/-{isd:5.3f}{pm:8.3f} +/-{psd:5.3f}{rm:8.3f} +/-{rsd:5.3f}")
for metric in ("iptm", "ptm"):
    ps = perseed_top(metric); oth = [x for s in SUBS[:3] for x in ps[s]]
    obs, p = exact_perm(ps["gap2nt"], oth)
    print(f"  2-nt gap {metric.upper()} {np.mean(ps['gap2nt']):.3f} vs others {np.mean(oth):.3f}  "
          f"(delta {obs:+.3f}; exact one-sided permutation p = {p:.1e}, 5 vs 15 seeds)")


print("\nwrote:")
for f in ("AF3_perModel_results.tsv", "AF3_summary_confidence.tsv"):
    print(f"  output/{f}")
