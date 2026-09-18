"""
PaCas3 domain architecture bar (matplotlib), with grey dots marking residues
that contact AcrIC3 (<= 8 A, computed in compute_interface.py) - as described in the methods.

INPUT: interface_residues.json (from compute_interface.py).
OUTPUT: PanelB_domain_bar.png (transparent). Run: python3 build_domain_bar.py from this folder.
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# (start, end, fill colour, label) - boundaries transferred from T. fusca Cas3 (PDB 4QQZ).
# Colours match the PyMOL domain colouring in build_panel_b.py.
DOMAINS = [
    (1, 216, "#ffff00", "HD"),
    (217, 430, "#00ffff", "RecA1"),
    (431, 602, "#228b22", "RecA2"),
    (603, 649, "#ffb6c1", "Linker"),
    (650, 744, "#ff00ff", "CTD"),
]
TOTAL = 744   # PaCas3 length (aa)

# Residue numbers of PaCas3 within 8 A of AcrIC3.
with open("interface_residues.json") as f:
    contacts = json.load(f)

fig, ax = plt.subplots(figsize=(13, 1.6), dpi=300)  # longer bar

bar_y = 0.0
bar_h = 0.6

# Draw each domain as a labelled box along the sequence axis.
for start, end, color, name in DOMAINS:
    ax.add_patch(Rectangle((start, bar_y), end - start, bar_h,
                            facecolor=color, edgecolor="black", linewidth=0.8))
    mid = (start + end) / 2
    text_color = "black"
    ax.text(mid, bar_y + bar_h / 2, name, ha="center", va="center",
            fontsize=13, color=text_color, family="serif", fontweight="bold")

# small grey dots above the bar for each AcrIC3-contacting residue (was tick lines)
dot_y = bar_y + bar_h + 0.12
ax.scatter(contacts, [dot_y] * len(contacts), s=6, color="grey", zorder=3)

# boundary numbers below the bar
for x in [216, 430, 602, 649, 744]:
    ax.text(x, bar_y - 0.12, str(x), ha="center", va="top", fontsize=12, family="serif", fontweight="bold")
    ax.plot([x, x], [bar_y, bar_y - 0.05], color="black", linewidth=0.6)

ax.set_xlim(-10, TOTAL + 10)
ax.set_ylim(-0.4, bar_y + bar_h + 0.3)
ax.axis("off")

plt.tight_layout()
plt.savefig("PanelB_domain_bar.png", dpi=300, transparent=True)
print("saved PanelB_domain_bar.png")
