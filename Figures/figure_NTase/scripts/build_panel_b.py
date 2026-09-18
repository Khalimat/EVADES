#!/usr/bin/env python3
"""Build Figure/NTase_B.png: the conserved nucleotidyltransferase (Pol-beta-like)
catalytic-motif alignment for the two NTases, GSx-AY[GAN]Tx4-SDxD-NPxh2[DE].

The motif and the per-residue match/mismatch calls below were taken directly
from the published Figure 4B (reverse-engineered pixel-by-pixel from
Figure/NTase_B.png: for each protein, blue = residue matches the motif's
required letter/bracket-set at that position, red = it doesn't, and the
motif's own "x"/"x4" wildcard slots are unscored (gray) EXCEPT the single "x"
between "NP" and "h2[DE]" (E88 / N95), which the original coloured black --
kept as-is for fidelity even though its scoring role (excluded from the X/14
tally, like the gray positions) is otherwise identical to a gray "x").
Reproducing this bar chart of matches independently confirms the reported
scores: 10/14 (YP_009091875.1) and 11/14 (YP_009031408.1).

Run: python3 scripts/build_panel_b.py
"""
import os
import matplotlib.pyplot as plt
from matplotlib import font_manager

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PNG = os.path.join(REPO, "Figure", "NTase_B.png")

BLUE = "#636EFA"    # matches motif requirement at this position
RED = "#EF553B"     # does not match
GRAY = "#C7C7C7"    # unscored wildcard ("x" / "x4")
BLACK = "#000000"   # unscored, but singled out in the original (see docstring)
NUM_GRAY = "#4D4D4D"
DOT_GRAY = "#838383"   # YP_009091875.1 (Erinnyis ello granulovirus)
DOT_SALMON = "#F59494"  # YP_009031408.1 (phage Bcp1)

FONT = "Times New Roman"
if FONT not in {f.name for f in font_manager.fontManager.ttflist}:
    FONT = "serif"  # fall back to matplotlib's default serif if TNR isn't installed

# Each row is a list of (block) where a block is a list of (resi, letter, color).
# Blocks are rendered with a gap between them, matching the original layout.
TOP = [  # YP_009091875.1 (Erinnyis ello granulovirus), 10/14
    [(9, "G", BLUE), (10, "S", BLUE), (11, "R", GRAY), (12, "A", BLUE), (13, "K", RED)],
    [(14, "G", BLUE)],
    [(15, "Y", RED), (16, "A", GRAY), (17, "V", GRAY), (18, "E", GRAY), (19, "S", GRAY),
     (20, "S", BLUE), (21, "D", BLUE), (22, "F", GRAY), (23, "D", BLUE)],
    [(86, "N", BLUE), (87, "P", BLUE), (88, "E", BLACK), (89, "L", BLUE), (90, "G", RED), (91, "V", RED)],
]
TOP_SCORE = "10/14"

BOTTOM = [  # YP_009031408.1 (phage Bcp1), 11/14
    [(24, "G", BLUE), (25, "S", BLUE), (26, "R", GRAY), (27, "L", RED), (28, "Y", BLUE)],
    [(29, "G", BLUE)],
    [(30, "T", BLUE), (31, "D", GRAY), (32, "T", GRAY), (33, "E", GRAY), (34, "N", GRAY),
     (35, "S", BLUE), (36, "D", BLUE), (37, "W", GRAY), (38, "D", BLUE)],
    [(93, "V", RED), (94, "P", BLUE), (95, "N", BLACK), (96, "N", RED), (97, "I", BLUE), (98, "E", BLUE)],
]
BOTTOM_SCORE = "11/14"

MOTIF = [
    [("GS", BLACK), ("x", GRAY)],
    [("AY[GAN]T", BLACK)],
    [("x4", GRAY), ("SD", BLACK), ("x", GRAY), ("D", BLACK)],
    [("NP", BLACK), ("x", GRAY), ("h2[DE]", BLACK)],
]

LETTER_W = 0.62      # nominal advance per residue letter, in data units
BLOCK_GAP = 0.9       # extra gap between blocks
ROW_Y = {"top": 2.0, "motif": 1.0, "bottom": 0.0}
FONT_SIZE = 26
NUM_FONT_SIZE = 13


def draw_residue_row(ax, blocks, y, numbers_above):
    """blocks: list of blocks of (resi, letter, color). Draws letters plus
    small resi numbers above (numbers_above=True) or below the row."""
    x = 0.0
    num_y = y + 0.62 if numbers_above else y - 0.62
    va = "bottom" if numbers_above else "top"
    for block in blocks:
        for resi, letter, color in block:
            ax.text(x, y, letter, fontsize=FONT_SIZE, family=FONT, color=color,
                     ha="left", va="center", fontweight="bold" if color != GRAY else "normal")
            ax.text(x + LETTER_W * 0.5 * len(letter), num_y, str(resi), fontsize=NUM_FONT_SIZE,
                     family=FONT, color=NUM_GRAY, ha="center", va=va)
            x += LETTER_W * len(letter)
        x += BLOCK_GAP
    return x


def draw_motif_row(ax, blocks, y):
    x = 0.0
    for block in blocks:
        for text, color in block:
            ax.text(x, y, text, fontsize=FONT_SIZE, family=FONT, color=color,
                     ha="left", va="center", fontweight="bold")
            x += LETTER_W * len(text)
        x += BLOCK_GAP
    return x


def main():
    fig, ax = plt.subplots(figsize=(11.3, 2.3), dpi=100)
    ax.set_xlim(-1.4, 20.5)
    ax.set_ylim(-1.0, 3.0)
    ax.axis("off")

    end_x = draw_residue_row(ax, TOP, ROW_Y["top"], numbers_above=True)
    ax.text(end_x + 0.3, ROW_Y["top"], TOP_SCORE, fontsize=20, family=FONT,
             color=NUM_GRAY, ha="left", va="center")

    ax.text(-1.35, ROW_Y["motif"], "Motif", fontsize=18, family=FONT,
             color=NUM_GRAY, ha="left", va="center")
    draw_motif_row(ax, MOTIF, ROW_Y["motif"])

    end_x = draw_residue_row(ax, BOTTOM, ROW_Y["bottom"], numbers_above=False)
    ax.text(end_x + 0.3, ROW_Y["bottom"], BOTTOM_SCORE, fontsize=20, family=FONT,
             color=NUM_GRAY, ha="left", va="center")

    # species dots at the start of each protein row
    ax.scatter([-0.45], [ROW_Y["top"]], s=340, color=DOT_GRAY, zorder=5, clip_on=False)
    ax.scatter([-0.45], [ROW_Y["bottom"]], s=340, color=DOT_SALMON, zorder=5, clip_on=False)

    fig.tight_layout(pad=0.2)
    fig.savefig(OUT_PNG, dpi=300, facecolor="white")
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
