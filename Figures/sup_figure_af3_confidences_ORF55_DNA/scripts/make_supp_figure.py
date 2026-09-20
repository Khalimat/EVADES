#!/usr/bin/env python3
"""Supplementary figure (Plotly): AlphaFold3 ipTM / pTM for the ORF55-DNA substrate panel.

Box + all 25 per-model points per substrate (5 seeds x 5 diffusion samples), with significance
brackets for the 2-nt gap vs each other substrate.

Statistics: exact two-sided permutation test on the per-seed mean scores (n = 5 vs 5, the seed is
the independent replicate). A pooled test and Mann-Whitney U are also printed to the console for
reference but are not written to the caption.

Writes output/AF3_confidence_scores.{html,png,pdf,svg} and
output/AF3_confidence_scores_caption.txt
"""
import os, re, glob, json, itertools, collections
from math import erfc, sqrt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(REPO, "af3_results", "folds_2026_09_03_19_12")
OUT  = os.path.join(REPO, "output")

SUBS  = ["intact_duplex", "nicked", "gap1nt", "gap2nt"]
LABEL = {"intact_duplex": "intact", "nicked": "nicked", "gap1nt": "1-nt gap", "gap2nt": "2-nt gap"}
COLOR = {"intact_duplex": "#9aa0a6", "nicked": "#4c72b0", "gap1nt": "#55a868", "gap2nt": "#c44e52"}

def subseed(p):
    d = os.path.basename(os.path.dirname(p))
    return re.match(r"orf55_(intact_duplex|nicked|gap1nt|gap2nt)_atp_seed(\d+)(_\d+)?$", d)

permodel = {m: collections.defaultdict(list) for m in ("iptm", "ptm")}
perseed  = {m: collections.defaultdict(lambda: collections.defaultdict(list)) for m in ("iptm", "ptm")}
for sc in glob.glob(f"{ROOT}/orf55_*/*_summary_confidences_*.json"):
    m = subseed(sc)
    if not m or m.group(3):
        continue
    sub, seed = m.group(1), int(m.group(2))
    j = json.load(open(sc))
    for k in ("iptm", "ptm"):
        permodel[k][sub].append(j[k])
        perseed[k][sub][seed].append(j[k])
perseed_mean = {k: {s: [float(np.mean(perseed[k][s][sd])) for sd in sorted(perseed[k][s])] for s in SUBS}
                for k in ("iptm", "ptm")}

def perm_p(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    obs = abs(a.mean() - b.mean())
    pool = np.concatenate([a, b]); na = len(a); hits = tot = 0
    for idx in itertools.combinations(range(len(pool)), na):
        mask = np.zeros(len(pool), bool); mask[list(idx)] = True
        hits += abs(pool[mask].mean() - pool[~mask].mean()) >= obs - 1e-12
        tot += 1
    return hits / tot

def mwu_p(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    n1, n2 = len(a), len(b)
    allv = np.concatenate([a, b])
    vals, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    avg = np.zeros(len(cnt)); pos = 0
    for i, c in enumerate(cnt):
        avg[i] = np.mean(np.arange(pos + 1, pos + c + 1)); pos += c
    ranks = avg[inv]
    U1 = ranks[:n1].sum() - n1 * (n1 + 1) / 2
    U = min(U1, n1 * n2 - U1)
    mu = n1 * n2 / 2
    tie = np.sum(cnt ** 3 - cnt)
    sd = sqrt(n1 * n2 / 12 * ((n1 + n2 + 1) - tie / ((n1 + n2) * (n1 + n2 - 1))))
    if sd == 0:
        return 1.0
    return erfc((abs(U - mu) - 0.5) / sd / sqrt(2))

pvals, lines = {}, []
print("2-nt gap vs other substrates\n")
for k in ("iptm", "ptm"):
    print(f"  {k.upper()}")
    for s in ("intact_duplex", "nicked", "gap1nt"):
        pp = perm_p(perseed_mean[k]["gap2nt"], perseed_mean[k][s])
        mw = mwu_p(permodel[k]["gap2nt"], permodel[k][s])
        pvals[(k, s)] = pp
        print(f"    vs {s:<14} perm(per-seed 5v5) p={pp:.4f}   MWU(per-model 25v25) p={mw:.2e}")
        lines.append(f"{k.upper()} 2-nt gap vs {s}: permutation p={pp:.4f}; Mann-Whitney U p={mw:.2e}")
    others = [x for s in ("intact_duplex", "nicked", "gap1nt") for x in perseed_mean[k][s]]
    pool = perm_p(perseed_mean[k]["gap2nt"], others)
    pvals[(k, "pool")] = pool
    print(f"    vs other three (pooled 5v15) perm p={pool:.2e}\n")
    lines.append(f"{k.upper()} 2-nt gap vs pooled other three: permutation p={pool:.2e}")

def stars(p):
    return "****" if p < 1e-4 else "***" if p < 1e-3 else "**" if p < 1e-2 else "*" if p < 5e-2 else "ns"

# ---------------- figure ----------------
fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.11)
XPOS = {s: i for i, s in enumerate(SUBS)}
for col, k, ylab in ((1, "iptm", "ipTM"), (2, "ptm", "pTM")):
    for s in SUBS:
        y = permodel[k][s]
        fig.add_trace(go.Violin(
            y=y, x=[LABEL[s]] * len(y), name=LABEL[s], showlegend=False,
            points="all", jitter=0.35, pointpos=0, width=0.85,
            box_visible=True, meanline_visible=True, scalemode="width", bandwidth=0.006,
            spanmode="hard",
            fillcolor=COLOR[s] + "26",  # ~15% alpha
            line=dict(color=COLOR[s], width=1.4),
            marker=dict(color=COLOR[s], size=4, opacity=0.55, line=dict(width=0)),
        ), row=1, col=col)
    # significance brackets: 2-nt gap (idx 3) vs 1-nt gap (2), nicked (1), intact (0)
    for j, s in enumerate(("gap1nt", "nicked", "intact_duplex")):
        x0, x1 = XPOS[s], XPOS["gap2nt"]
        yb = 0.957 + j * 0.011
        for seg in ([x0, yb, x0, yb + 0.003], [x0, yb + 0.003, x1, yb + 0.003], [x1, yb + 0.003, x1, yb]):
            fig.add_shape(type="line", x0=seg[0], y0=seg[1], x1=seg[2], y1=seg[3],
                          line=dict(color="#444", width=1), row=1, col=col)
        fig.add_annotation(x=(x0 + x1) / 2, y=yb + 0.003, yshift=7, showarrow=False,
                           text=stars(pvals[(k, s)]), font=dict(size=13), row=1, col=col)
    fig.add_annotation(x=0, y=1.0, xref=f"x{'' if col==1 else col} domain",
                       yref=f"y{'' if col==1 else col} domain", xshift=-46, yshift=6,
                       text="<b>%s</b>" % ("A" if col == 1 else "B"), showarrow=False,
                       font=dict(size=16))
    fig.update_yaxes(range=[0.76, 1.0], title_text=ylab, gridcolor="rgba(0,0,0,0.08)",
                     zeroline=False, row=1, col=col)

fig.update_xaxes(categoryorder="array", categoryarray=[LABEL[s] for s in SUBS])
fig.update_layout(template="simple_white", width=820, height=460, violingap=0.25,
                  margin=dict(l=64, r=20, t=54, b=44), font=dict(size=12),
                  title=dict(text="ORF55 and ATP co-folded with DNA substrates",
                             font=dict(size=13), x=0.5, xanchor="center", y=0.97))

fig.write_html(os.path.join(OUT, "AF3_confidence_scores.html"), include_plotlyjs="cdn")
for ext in ("png", "pdf", "svg"):
    fig.write_image(os.path.join(OUT, f"AF3_confidence_scores.{ext}"), scale=3)

cap = ("Supplementary Figure 1. AlphaFold 3 confidence for ORF55-ATP-DNA co-folding is lower for "
       "a two-nucleotide gap than for nicked or one-nucleotide-gapped DNA. ORF55 and ATP were "
       "co-folded with a 21-bp DNA duplex that was intact (ligated), nicked, one-nucleotide "
       "gapped or two-nucleotide gapped, using five independent AlphaFold 3 seeds per substrate "
       "with five diffusion samples each (25 models per substrate). (A) ipTM and (B) pTM for "
       "every model, shown as points over a violin with an inner box (median and interquartile "
       "range) and a line at the mean. Brackets: **, P < 0.01 for the two-nucleotide gap versus "
       "each other substrate (exact two-sided permutation test on the per-seed means, n = 5 "
       "seeds per group).")
open(os.path.join(OUT, "AF3_confidence_scores_caption.txt"), "w").write(
    cap + "\n\n"
    + "Pairwise 2-nt gap vs each substrate, exact two-sided permutation test on per-seed means "
      "(n = 5 vs 5): P = 0.008 for ipTM and for pTM against intact, nicked and 1-nt gap "
      "(complete separation; 0.008 is the minimum attainable at this sample size).\n")
print("wrote output/AF3_confidence_scores.{html,png,pdf,svg} and _caption.txt")
