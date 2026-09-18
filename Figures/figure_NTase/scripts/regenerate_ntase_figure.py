#!/usr/bin/env python3
"""Regenerate Figure/NTase_figure.png with its panel C swapped for the updated
AF3 confidence-score figure.

Figure/NTase_figure.svg is a hand-assembled Inkscape composite (panels A/B/C/D +
their "A"/"B"/"C"/"D" labels as separate top-level objects in one flat layer).
Panel C is the matplotlib heatmap group with id="figure_1" (originally exported
from an older version of make_supp_figure.py); see the docstring of
make_supp_figure.py for why it is replaced by
supplementary/AF3_confidence_scores.png (per-seed violin plots over all 10 NTP
pairs incl. CTP, with permutation-test stats, instead of a single-model-per-cell
heatmap over 6 pairs).

This script:
  1. Uses Inkscape's CLI to find panel C's on-page bounding box (object id
     "figure_1", or "panelC_AF3_confidence" if this script already ran once).
  2. Replaces that object in the SVG with an embedded (base64) copy of
     supplementary/AF3_confidence_scores.png, scaled to fit the same bounding
     box width (preserving the new image's aspect ratio, vertically centered
     in the old bbox) so panels A/B/D and the panel labels are untouched.
  3. Re-exports the SVG to PNG at 250 dpi (the dpi the original PNG was
     exported at -- see inkscape:export-xdpi/-ydpi in the SVG), overwriting
     Figure/NTase_figure.png.

Backs up whatever it overwrites (NTase_figure.svg -> .svg.bak,
NTase_figure.png -> .png.bak) so a re-run is non-destructive. Safe to re-run:
if the replacement image is already in place, it is updated in place rather
than duplicated.

Usage: python3 scripts/regenerate_ntase_figure.py
"""
import base64
import os
import re
import shutil
import subprocess
import sys

from lxml import etree

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURE_DIR = os.path.join(REPO, "Figure")
SVG_PATH = os.path.join(FIGURE_DIR, "NTase_figure.svg")
PNG_PATH = os.path.join(FIGURE_DIR, "NTase_figure.png")
REPLACEMENT_PNG = os.path.join(REPO, "Figure", "panelC_AF3_confidence_scores.png")

OLD_PANEL_C_ID = "figure_1"
NEW_PANEL_C_ID = "panelC_AF3_confidence"
EXPORT_DPI = 250  # matches inkscape:export-xdpi/-ydpi already set in the SVG

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
NSMAP = {"svg": SVG_NS, "xlink": XLINK_NS}


def find_inkscape():
    candidates = [
        shutil.which("inkscape"),
        "/Applications/Inkscape.app/Contents/MacOS/inkscape",
        "/usr/bin/inkscape",
        "/opt/homebrew/bin/inkscape",
    ]
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    raise RuntimeError(
        "Could not find an Inkscape executable. Install it (e.g. `brew install "
        "--cask inkscape`) or edit find_inkscape() with its path."
    )


def query_bbox_mm(inkscape, svg_path, object_id):
    """Bounding box (x, y, width, height) of `object_id`, in the SVG's own user
    units (this document declares width="532mm" height="597mm" with a matching
    viewBox, so 1 user unit == 1 mm). Inkscape's --query-* flags report in
    96-dpi px regardless of document units, hence the /96*25.4 conversion."""
    out = subprocess.run(
        [
            inkscape,
            f"--query-id={object_id}",
            "--query-x", "--query-y", "--query-width", "--query-height",
            svg_path,
        ],
        capture_output=True, text=True, check=True,
    ).stdout.strip().splitlines()
    if len(out) != 4:
        raise RuntimeError(f"Unexpected --query output for id={object_id!r}: {out}")
    x_px, y_px, w_px, h_px = (float(v) for v in out)
    px_to_mm = 25.4 / 96.0
    return x_px * px_to_mm, y_px * px_to_mm, w_px * px_to_mm, h_px * px_to_mm


def png_pixel_size(png_path):
    from PIL import Image
    with Image.open(png_path) as im:
        return im.size  # (width, height)


def main():
    if not os.path.isfile(SVG_PATH):
        sys.exit(f"Missing {SVG_PATH}")
    if not os.path.isfile(REPLACEMENT_PNG):
        sys.exit(f"Missing {REPLACEMENT_PNG}")

    inkscape = find_inkscape()

    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(SVG_PATH, parser)
    root = tree.getroot()

    old_group = root.find(f'.//svg:g[@id="{OLD_PANEL_C_ID}"]', NSMAP)
    old_image = root.find(f'.//svg:image[@id="{NEW_PANEL_C_ID}"]', NSMAP)
    if old_group is None and old_image is None:
        sys.exit(
            f"Could not find panel C ({OLD_PANEL_C_ID!r} or {NEW_PANEL_C_ID!r}) "
            f"in {SVG_PATH}; the file's structure may have changed."
        )

    query_id = OLD_PANEL_C_ID if old_group is not None else NEW_PANEL_C_ID
    bbox_x, bbox_y, bbox_w, bbox_h = query_bbox_mm(inkscape, SVG_PATH, query_id)
    print(f"Panel C bounding box (mm): x={bbox_x:.3f} y={bbox_y:.3f} "
          f"w={bbox_w:.3f} h={bbox_h:.3f}")

    img_w_px, img_h_px = png_pixel_size(REPLACEMENT_PNG)
    aspect = img_w_px / img_h_px

    # Fit to the old bbox's width (never overflows sideways into panel D),
    # preserve aspect ratio, and vertically center in the old bbox's height.
    new_w = bbox_w
    new_h = new_w / aspect
    new_x = bbox_x
    new_y = bbox_y + (bbox_h - new_h) / 2.0
    print(f"Placing replacement image (mm): x={new_x:.3f} y={new_y:.3f} "
          f"w={new_w:.3f} h={new_h:.3f}")

    with open(REPLACEMENT_PNG, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    href = f"data:image/png;base64,{b64}"

    new_image = etree.Element(f"{{{SVG_NS}}}image")
    new_image.set("id", NEW_PANEL_C_ID)
    new_image.set("x", repr(new_x))
    new_image.set("y", repr(new_y))
    new_image.set("width", repr(new_w))
    new_image.set("height", repr(new_h))
    new_image.set("preserveAspectRatio", "none")
    new_image.set(f"{{{XLINK_NS}}}href", href)

    if old_group is not None:
        parent = old_group.getparent()
        parent.replace(old_group, new_image)
    else:
        parent = old_image.getparent()
        parent.replace(old_image, new_image)

    svg_backup = SVG_PATH + ".bak"
    if not os.path.exists(svg_backup):
        shutil.copy2(SVG_PATH, svg_backup)
    tree.write(SVG_PATH, xml_declaration=True, encoding="UTF-8", standalone=False)
    print(f"Updated {SVG_PATH} (original backed up to {svg_backup})")

    if os.path.isfile(PNG_PATH):
        png_backup = PNG_PATH + ".bak"
        if not os.path.exists(png_backup):
            shutil.copy2(PNG_PATH, png_backup)

    subprocess.run(
        [
            inkscape,
            f"--export-dpi={EXPORT_DPI}",
            "--export-type=png",
            f"--export-filename={PNG_PATH}",
            SVG_PATH,
        ],
        check=True,
    )
    w, h = png_pixel_size(PNG_PATH)
    print(f"Wrote {PNG_PATH} ({w}x{h}px @ {EXPORT_DPI}dpi)")


if __name__ == "__main__":
    main()
