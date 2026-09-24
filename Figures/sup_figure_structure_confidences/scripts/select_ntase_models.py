"""List the top-ranking_score NTase models (5 seeds x 5 samples each).

AlphaFold Server rounds ranking_score to 2 decimals, so several models tie at the top.
The figure uses the first top hit found at the time: YP_009031408 seed4 / model 0 and
YP_009091875 seed2 / model 1 (see targets.py). Tied models are near-identical in ipTM/pTM.
"""
import glob, json, os
from targets import NT

for acc in ("yp_009031408", "yp_009091875"):
    rows = []
    for p in sorted(glob.glob(os.path.join(NT, f"ntase_{acc}_utp_utp_mg3_seed*", "*summary_confidences_*.json"))):
        sc = json.load(open(p))
        rows.append((sc["ranking_score"], sc.get("iptm"), sc.get("ptm"), os.path.basename(p)))
    top = max(r[0] for r in rows)
    print(f"{acc}: top ranking_score = {top:.2f}")
    for r in rows:
        if r[0] == top:
            print("   ipTM=%.2f pTM=%.2f  %s" % (r[1], r[2], r[3]))
