#!/usr/bin/env python3
"""Build Figure/NTase_A.png: cartoon superposition of the two NTase structures
in two orientations 180 degrees apart, with a color legend.

Needs a PRE-SUPERPOSED two-chain structure (chain A = phage Bcp1 YP_009031408.1,
chain B = Erinnyis ello granulovirus YP_009091875.1) -- see SUPERPOSED_PDB
below. This repo's own AF3 predictions (af3_results/) only ever model each
NTase in complex with an NTP pair, so getting a clean apo-vs-apo superposition
of the two proteins alone is a separate structural-alignment step, done once
outside this script; the result is expected at the path below.

Colors (sampled directly from the published Figure 4A legend swatches):
  gray  #838383 = Erinnyis ello granulovirus (YP_009091875.1)
  salmon #F59494 = phage Bcp1 (YP_009031408.1)

Run: python3 scripts/build_panel_a.py
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "scripts")
OUT_PNG = os.path.join(REPO, "Figure", "NTase_A.png")

SUPERPOSED_PDB = os.path.join(REPO, "structures", "ntase_YP_009091875.pdb")
VIEW_JSON = os.path.join(REPO, "Figure", "_panelA_view.json")

PYMOL_CANDIDATES = [
    "/Applications/PyMOL.app/Contents/bin/pymol",
    "/usr/bin/pymol",
    "/opt/homebrew/bin/pymol",
]

GRAY = (131, 131, 131)
SALMON = (245, 148, 148)
BG = (255, 255, 255)


def find_pymol():
    from shutil import which
    for c in [which("pymol")] + PYMOL_CANDIDATES:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    raise RuntimeError("Could not find a PyMOL executable; edit PYMOL_CANDIDATES.")


def load_font(size, bold=False):
    names = (
        ["Times New Roman Bold.ttf", "Times New Roman.ttf"] if bold
        else ["Times New Roman.ttf"]
    )
    for name in names:
        for base in ("/System/Library/Fonts/Supplemental", "/Library/Fonts"):
            path = os.path.join(base, name)
            if os.path.isfile(path):
                return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_rotation_icon(draw, cx, cy, r):
    draw.arc([cx - r, cy - r, cx + r, cy + r], start=30, end=300, fill="black", width=3)
    draw.line([cx - r * 1.4, cy, cx + r * 1.4, cy], fill="black", width=3)
    draw.line([cx, cy - r * 1.4, cx, cy + r * 1.4], fill="black", width=3)


def main():
    if not os.path.isfile(SUPERPOSED_PDB):
        sys.exit(
            f"Missing pre-superposed structure at {SUPERPOSED_PDB}\n"
            "This script does not compute the alignment itself -- see the "
            "module docstring."
        )

    pymol = find_pymol()
    view1 = os.path.join(REPO, "Figure", "_panelA_view1.png")
    view2 = os.path.join(REPO, "Figure", "_panelA_view2.png")
    subprocess.run(
        [pymol, "-cq", os.path.join(SCRIPTS, "_pymol_render_panel_a.py"),
         "--", SUPERPOSED_PDB, view1, view2, VIEW_JSON],
        check=True,
    )

    im1 = Image.open(view1).convert("RGB")
    im2 = Image.open(view2).convert("RGB")

    def trim(im, bg=BG, pad=20):
        from PIL import ImageChops
        diff = ImageChops.difference(im, Image.new("RGB", im.size, bg))
        bbox = diff.getbbox()
        if not bbox:
            return im
        x0, y0, x1, y1 = bbox
        x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
        x1, y1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
        return im.crop((x0, y0, x1, y1))

    im1, im2 = trim(im1), trim(im2)
    h = max(im1.height, im2.height)
    im1 = im1.resize((round(im1.width * h / im1.height), h))
    im2 = im2.resize((round(im2.width * h / im2.height), h))

    gap = 260  # room for the rotation icon
    legend_h = 220
    W = im1.width + gap + im2.width
    H = h + legend_h
    canvas = Image.new("RGB", (W, H), BG)
    canvas.paste(im1, (0, 0))
    canvas.paste(im2, (im1.width + gap, 0))

    draw = ImageDraw.Draw(canvas)
    icon_cx = im1.width + gap // 2
    icon_cy = h // 2
    draw.text((icon_cx, icon_cy - 60), "180°", font=load_font(34), fill="black", anchor="mm")
    draw_rotation_icon(draw, icon_cx, icon_cy + 10, 30)

    # legend
    lx, ly = 20, h + 30
    draw.text((lx, ly), "NTase", font=load_font(30, bold=True), fill="black")
    dot_r = 20
    ly2 = ly + 55
    draw.ellipse([lx, ly2, lx + 2 * dot_r, ly2 + 2 * dot_r], fill=GRAY)
    draw.text((lx + 2 * dot_r + 15, ly2 - 5), "Erinnyis ello granulovirus",
              font=load_font(26), fill="black")
    draw.text((lx + 2 * dot_r + 15, ly2 + 30), "(YP_009091875.1)",
              font=load_font(26), fill="black")

    lx2 = lx + 620
    draw.ellipse([lx2, ly2, lx2 + 2 * dot_r, ly2 + 2 * dot_r], fill=SALMON)
    draw.text((lx2 + 2 * dot_r + 15, ly2 - 5), "Phage Bcp1",
              font=load_font(26), fill="black")
    draw.text((lx2 + 2 * dot_r + 15, ly2 + 30), "(YP_009031408.1)",
              font=load_font(26), fill="black")

    canvas.save(OUT_PNG)
    os.remove(view1)
    os.remove(view2)
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
