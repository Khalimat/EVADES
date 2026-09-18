"""Assemble Figure 3 from the PyMOL renders (pure matplotlib, no PyMOL).

  Panel A : 2 rows x 2 columns of structure views
            row 1  ORF55 + DNA            (AlphaFold 3)
            row 2  Chlorella ligase + DNA (PDB 2Q2U)
            column 2 is column 1 rotated 90 deg about the horizontal axis
            (DNA: blue backbone tube + base-pair sticks)
  Panel B : residue-by-residue ORF55 (coral) vs Chlorella-virus ligase (grey)
            - adenylylation active site (8)         02_render_panelB.py
            - nick recognition (2)
            - substrate & clamp geometry (3)
            - OB-domain latch: global overview (latch gold in the superimposed
              folds) + magnified latch superposition   04_render_latch.py

INPUTS
  figures/panelA/row{1,2}_col{1,2}.png   from 01_render_panelA.py
  figures/panelB/<order>_<label>.png     from 02_render_panelB.py
  figures/latch/{context_1,zoom}.png     from 04_render_latch.py
  data/active_site_residues.tsv, data/latch_residues.tsv   labels, grouping, BLOSUM62 scores

Run:  python3 scripts/03_assemble_figure.py
Out:  figures/Figure3.png  figures/Figure3.pdf  figures/Figure3.svg
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Polygon, Rectangle
import numpy as np
from PIL import Image

for _c in (os.path.join(os.getcwd(), "scripts"),):
    if os.path.exists(os.path.join(_c, "figconfig.py")):
        sys.path.insert(0, _c)
        break
import figconfig as cfg

ROOT = os.path.dirname(sys.path[0])
PA   = os.path.join(ROOT, "figures", "panelA")
PB   = os.path.join(ROOT, "figures", "panelB")
PL   = os.path.join(ROOT, "figures", "latch")
OUT  = os.path.join(ROOT, "figures")

CORAL = cfg.ORF55_COLOR
GREY  = cfg.LIGASE_COLOR
GOLD  = "#E0A32B"                 # OB-domain latch highlight (matches 04_render_latch.py)
INK   = "#242424"
MUTE  = "#8c8c8c"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

# Figure size (inches) and layout constants, all in figure-fraction units:
# FW/FH = canvas width/height; L/R = left/right margins of the content area;
# CG = gap between neighbouring images.
FW, FH = 7.20, 8.6
L, R = 0.052, 0.992
CG = 0.006


# --------------------------------------------------------------- helpers ------
def load_img(path, crop=True, pad_frac=0.02):
    """Load a transparent PyMOL PNG onto white and (optionally) auto-crop the white
    margin, keeping `pad_frac` of padding. Returns an RGB numpy array."""
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    rgb = bg.convert("RGB")
    if crop:
        arr = np.asarray(rgb)
        mask = np.any(arr < 246, axis=2)
        if mask.any():
            ys, xs = np.where(mask)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            py = int((y1 - y0) * pad_frac) + 3
            px = int((x1 - x0) * pad_frac) + 3
            rgb = rgb.crop((max(0, x0 - px), max(0, y0 - py),
                            min(arr.shape[1], x1 + px), min(arr.shape[0], y1 + py)))
    return np.asarray(rgb)


def img_ax(fig, x, y, w, h, img):
    """Place *img* in box (x,y,w,h) [fig frac], preserving aspect, centred."""
    box_ar = (w * FW) / (h * FH)
    im_ar = img.shape[1] / img.shape[0]
    if im_ar > box_ar:
        dw, dh = w, w * FW / im_ar / FH
    else:
        dh, dw = h, h * FH * im_ar / FW
    ax = fig.add_axes([x + (w - dw) / 2, y + (h - dh) / 2, dw, dh])
    ax.imshow(img)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def rot_icon(fig, xc, yc):
    """'Rotate 90 deg' glyph: a thin dark-grey curved arrow whose head shows the
    direction, plus the angle."""
    dgrey = "#5a5a5a"
    r = 0.0135
    ax = fig.add_axes([xc - r, yc - r * FW / FH, 2 * r, 2 * r * FW / FH], zorder=6)
    ax.set_xlim(-1.4, 1.4); ax.set_ylim(-1.4, 1.4)
    ax.axis("off"); ax.set_aspect("equal")
    th = np.linspace(np.deg2rad(160), np.deg2rad(380), 60)
    ex, ey = 1.05 * np.cos(th), 0.62 * np.sin(th)
    ax.plot(ex, ey, color=dgrey, lw=1.0, solid_capstyle="round")
    p0 = np.array([ex[-1], ey[-1]])
    tang = p0 - np.array([ex[-6], ey[-6]])
    tang = tang / (np.hypot(*tang) + 1e-9)
    perp = np.array([-tang[1], tang[0]])
    ax.add_patch(Polygon([p0 + tang * 0.26,
                          p0 - tang * 0.08 + perp * 0.20,
                          p0 - tang * 0.08 - perp * 0.20],
                         closed=True, color=dgrey, lw=0))
    fig.text(xc + r + 0.003, yc, "90°", ha="left", va="center",
             fontsize=7.0, color=dgrey)


def colour_key(fig, kx, ky):
    """Draw the small colour legend (ORF55 / ligase / latch) with its top-left at (kx, ky)."""
    for i, (c, txt) in enumerate([
            (CORAL, "ORF55  (DruSM1 phage)"),
            (GREY,  "DNA ligase  (Chlorella virus)"),
            (GOLD,  "OB-domain latch")]):
        yy = ky - i * 0.017
        fig.patches.append(Rectangle((kx, yy), 0.013, 0.013 * FW / FH,
                                     transform=fig.transFigure,
                                     facecolor=c, edgecolor="none"))
        fig.text(kx + 0.020, yy + 0.0065 * FW / FH, txt, ha="left", va="center",
                 fontsize=7.0, color=INK)


# --------------------------------------------------------------- data --------
# Residue tables drive panel B: ordering, group, label, identity and BLOSUM62 score.
with open(os.path.join(ROOT, "data", "active_site_residues.tsv")) as fh:
    PAIRS = list(csv.DictReader(fh, delimiter="\t"))
with open(os.path.join(ROOT, "data", "latch_residues.tsv")) as fh:
    LATCH = list(csv.DictReader(fh, delimiter="\t"))

ROW_LABELS = ["ORF55 + DNA  (AF3)", "Ligase + DNA  (2Q2U)"]

# --------------------------------------------------------------- layout ------
fig = plt.figure(figsize=(FW, FH))
fig.patch.set_facecolor("white")

# ============================ Panel A : 2 rows x 2 columns ===================
ncol, nrow = cfg.N_COLS, 2
A_top = 0.990
ah, RG = 0.210, 0.004
A_bot = A_top - nrow * ah - (nrow - 1) * RG
aw = 0.405
ax0 = L + 0.012                                   # small indent past the "A"
for ri in range(nrow):
    y0 = A_top - ah - ri * (ah + RG)
    for ci in range(ncol):
        x0 = ax0 + ci * (aw + CG)
        img_ax(fig, x0, y0, aw, ah,
               load_img(os.path.join(PA, f"row{ri+1}_col{ci+1}.png"),
                        crop=True, pad_frac=0.03))
    fig.text(L - 0.012, y0 + ah / 2, ROW_LABELS[ri], rotation=90,
             ha="center", va="center", fontsize=7.0, color=MUTE)
    if ncol == 2:
        rot_icon(fig, ax0 + aw * 0.86, y0 + ah * 0.5)

fig.text(0.006, A_top + 0.003, "A", ha="left", va="top",
         fontsize=12, fontweight="bold", color=INK)
fig.add_artist(plt.Line2D([L, R], [A_bot - 0.010, A_bot - 0.010],
                          transform=fig.transFigure, color="#cfcfcf", lw=1.6))

# ============================ Panel B =======================================
A_B_GAP = 0.055                                   # (c) breathing room A -> B
fig.text(0.006, A_bot - A_B_GAP + 0.010, "B", ha="left", va="top",
         fontsize=12, fontweight="bold", color=INK)

pb_imgs = {p["order"]: load_img(
               os.path.join(PB, f"{p['order'].zfill(2)}_{p['label']}.png"),
               crop=True, pad_frac=0.012) for p in PAIRS}
BW = (R - L - 7 * CG) / 8                          # 8 insets across the full row
grouplab_pad = 0.030                               # header sits well above the residue labels
lab_pad = 0.006
row_v_gap = 0.056

by_group = {}
for p in PAIRS:
    by_group.setdefault(p["group"], []).append(p)


def group_header(x0, w, y_top, label):
    """Italic group title with a thin rule above a row of insets."""
    fig.text(x0, y_top + grouplab_pad, label, ha="left", va="bottom",
             fontsize=7.6, color=MUTE, style="italic")
    fig.add_artist(plt.Line2D([x0, x0 + w], [y_top + grouplab_pad - 0.009] * 2,
                              transform=fig.transFigure, color="#e9e9e9", lw=0.8))


def draw_cluster(items, x0, y_top):
    """Draw a row of residue insets (one group) left-to-right from x0; label each with
    its residue pair and BLOSUM62 score (non-identical pairs in italics).
    Returns the row height so callers can stack the next row below."""
    im0 = pb_imgs[items[0]["order"]]
    rh = max(BW * FW / (pb_imgs[p["order"]].shape[1]
                        / pb_imgs[p["order"]].shape[0]) / FH for p in items)
    group_header(x0, len(items) * BW + (len(items) - 1) * CG, y_top,
                 items[0]["group_label"])
    for k, p in enumerate(items):
        x = x0 + k * (BW + CG)
        img_ax(fig, x, y_top - rh, BW, rh, pb_imgs[p["order"]])
        lab = p["label"].replace("-", "–")
        if p["blosum62"]:                       # BLOSUM62 score (caption); non-identical pairs only
            v = int(p["blosum62"])
            lab += f"  ({'+' if v > 0 else '−'}{abs(v)})"
        fig.text(x + BW / 2, y_top + lab_pad, lab, ha="center", va="bottom",
                 fontsize=7.0, color=INK,
                 style="italic" if p["identical"] == "no" else "normal")
    return rh


y = A_bot - A_B_GAP - 0.010

g = by_group["active_site"]
y -= draw_cluster(g, L, y) + row_v_gap

gA, gB = by_group["nick_recognition"], by_group["structural"]
wB = len(gB) * BW + (len(gB) - 1) * CG
row_top = y
rh = max(draw_cluster(gA, L, row_top), draw_cluster(gB, R - wB, row_top))
colour_key(fig, L + len(gA) * BW + CG + 0.055, row_top - rh * 0.30)
y = row_top - rh - row_v_gap

# ---- OB-domain latch : global overview + magnified ----
group_header(L, R - L, y, "OB-domain latch  (residues 202–231)")
y -= 0.006

ctx = load_img(os.path.join(PL, "context_1.png"), crop=True, pad_frac=0.03)
zm  = load_img(os.path.join(PL, "zoom.png"),      crop=True, pad_frac=0.03)
lh, lgap = 0.205, 0.050                              # shared height drives the widths
lw1 = lh * FH * (ctx.shape[1] / ctx.shape[0]) / FW
lw2 = lh * FH * (zm.shape[1] / zm.shape[0]) / FW
lx0 = L + (R - L - lw1 - lw2 - lgap) / 2
img_ax(fig, lx0, y - lh, lw1, lh, ctx)
img_ax(fig, lx0 + lw1 + lgap, y - lh, lw2, lh, zm)
fig.text(lx0 + lw1 / 2, y - lh - 0.004,
         "the latch (gold) in the two superimposed folds",
         ha="center", va="top", fontsize=6.6, color=MUTE)
fig.text(lx0 + lw1 + lgap + lw2 / 2, y - lh - 0.004,
         "magnified — ORF55 (coral) over the ligase (grey)",
         ha="center", va="top", fontsize=6.6, color=MUTE)
y -= lh + 0.020

# Export: 600-dpi PNG plus vector PDF/SVG (text kept as text: svg.fonttype=none).
for ext in ("png", "pdf", "svg"):
    fig.savefig(os.path.join(OUT, f"Figure3.{ext}"),
                dpi=600 if ext == "png" else None, facecolor="white",
                bbox_inches="tight", pad_inches=0.03)
    print("wrote", os.path.join(OUT, f"Figure3.{ext}"))
plt.close(fig)
