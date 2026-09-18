#!/usr/bin/env python3
"""Reassemble the full two-part Panel D: a full-protein overview (active-site
residues colored, ligand/ions shown) with a box drawn around the active-site
region, connected by lines down to the magnified inset -- matching the
original figure's design (build_active_site_figure.py alone only produces
the inset, which isn't the whole panel).

Uses:
  - Figure/_panelD_overview_full.png + _panelD_crop_box.json, written by the
    last run of build_active_site_figure.py (the overview and the pixel box
    it cropped for the inset).
  - The inset image given on the command line -- pass whatever your final,
    possibly hand-edited-in-Inkscape, rasterized inset is (see
    merge_active_site_into_figure.py, which rasterizes active_site_labeled.svg
    for you automatically if you just want the current one).

Run: python3 scripts/assemble_panel_d_overview.py <inset.png> [output.png]
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURE_DIR = os.path.join(REPO, "Figure")
CROP_BOX_JSON = os.path.join(FIGURE_DIR, "_panelD_crop_box.json")
DEFAULT_OUT = os.path.join(FIGURE_DIR, "panelD_full.png")
BG = (255, 255, 255)
INSET_WIDTH_FRAC = 0.55  # inset width as a fraction of the overview's width


def trim(im, bg=BG, pad=20):
    diff = ImageChops.difference(im, Image.new("RGB", im.size, bg))
    bbox = diff.getbbox()
    if not bbox:
        return im, (0, 0)
    x0, y0, x1, y1 = bbox
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
    return im.crop((x0, y0, x1, y1)), (x0, y0)


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: assemble_panel_d_overview.py <inset.png> [output.png]")
    inset_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT

    if not os.path.isfile(CROP_BOX_JSON):
        sys.exit(f"Missing {CROP_BOX_JSON} -- run build_active_site_figure.py first.")
    meta = json.load(open(CROP_BOX_JSON))
    overview = Image.open(os.path.join(REPO, meta["overview"])).convert("RGB")
    inset = Image.open(inset_path).convert("RGB")

    overview_trimmed, (ox0, oy0) = trim(overview)
    box_x0, box_y0 = meta["x0"] - ox0, meta["y0"] - oy0
    box_x1, box_y1 = meta["x1"] - ox0, meta["y1"] - oy0

    inset_trimmed, _ = trim(inset)

    # Overview keeps its own natural width; the inset is scaled to a smaller
    # FRACTION of it (not stretched to match), matching the original figure
    # where the magnified box is clearly smaller than the full structure.
    W = overview_trimmed.width
    overview_r = overview_trimmed
    inset_w = round(W * INSET_WIDTH_FRAC)
    inset_h = round(inset_trimmed.height * inset_w / inset_trimmed.width)
    inset_r = inset_trimmed.resize((inset_w, inset_h))
    inset_x = (W - inset_w) // 2  # centered under the overview

    connector_h = 60
    H = overview_r.height + connector_h + inset_r.height
    canvas = Image.new("RGB", (W, H), BG)
    canvas.paste(overview_r, (0, 0))
    canvas.paste(inset_r, (inset_x, overview_r.height + connector_h))

    draw = ImageDraw.Draw(canvas)
    # box around the active-site region on the overview
    draw.rectangle([box_x0, box_y0, box_x1, box_y1], outline="black", width=3)
    # trapezoid connector down to the (now smaller, centered) inset
    y1 = overview_r.height + connector_h
    draw.line([(box_x0, box_y1), (inset_x, y1)], fill="black", width=2)
    draw.line([(box_x1, box_y1), (inset_x + inset_w, y1)], fill="black", width=2)
    draw.rectangle([inset_x, y1, inset_x + inset_w, y1 + inset_r.height], outline="black", width=3)

    canvas.save(out_path)
    print(f"wrote {out_path} ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    main()
