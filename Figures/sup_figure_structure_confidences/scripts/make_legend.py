"""Shared pLDDT colour key drawn once at the top of the figure."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from targets import RENDERS

os.makedirs(RENDERS, exist_ok=True)
OUT = os.path.join(RENDERS, "pLDDT_legend.png")

bins = [
    ("Very high (pLDDT > 90)", "#0053D6"),
    ("High (90 > pLDDT > 70)", "#65CBF3"),
    ("Low (70 > pLDDT > 50)", "#FFDB13"),
    ("Very low (pLDDT < 50)", "#FF7D45"),
]

fig, ax = plt.subplots(figsize=(16.5, 0.9))
ax.axis("off")

handles = [mpatches.Patch(facecolor=c, edgecolor="black", linewidth=0.5, label=l) for l, c in bins]
leg = ax.legend(handles=handles, ncol=4, loc="center", frameon=False,
                 fontsize=18, handlelength=1.4, handleheight=1.4,
                 columnspacing=2.2, handletextpad=0.6)

fig.savefig(OUT, dpi=300, bbox_inches="tight", pad_inches=0.05)
print("wrote", OUT)
