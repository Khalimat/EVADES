#!/usr/bin/env python3
"""Build Figure/active_site_labeled.{png,svg} from a saved PyMOL session
(default: active_site.pse), carrying over whatever camera angle, coloring,
and label positions/text you last set/dragged in that session.

How: renders the session three times headlessly, from its own saved camera
(see _pymol_render_active_site_svg.py) -- once clean, once with a small
uniquely-colored marker sphere at each active_blue residue's CA, and once
with each residue's real label re-shown one at a time in a unique color --
then finds each marker/label's actual on-screen pixel by color.

From there:
  - The image is cropped tightly to the active site itself (the bounding
    box of the residues' CAs and their labels, plus padding), not just
    whitespace-trimmed off the full protein render.
  - Each label starts at wherever you set it in PyMOL, but if it overlaps
    another label or sits mostly on top of the structure (non-white
    pixels in the clean render), it's nudged to the nearest nearby spot
    (spiral search) that clears both -- your placement is respected unless
    it's actually a problem.
Final SVG has the cropped structure as an embedded raster image and each
label as real, independently-editable vector <text> (open it in
Illustrator/Inkscape and you can drag the text directly).

Run: python3 scripts/build_active_site_figure.py [session.pse]
"""
import base64
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "scripts")
DEFAULT_SESSION = os.path.join(REPO, "active_site.pse")
OUT_PNG = os.path.join(REPO, "Figure", "active_site_labeled.png")
OUT_SVG = os.path.join(REPO, "Figure", "active_site_labeled.svg")
FONT_SCALE = 1.82  # multiplier on the detected PyMOL label size, for the SVG text
CROP_PAD = 130      # px padding around the residues+labels bounding box
STRUCTURE_OVERLAP_MAX = 0.12  # max fraction of a label's box allowed to sit on non-white pixels

# One-off manual nudges: {resi: degrees to rotate the label CCW (on screen)
# around its own CA}, applied to its auto-detected position before the
# collision-avoidance pass (which still gets the final say if the rotated
# spot turns out to overlap something).
MANUAL_ROTATIONS = {140: 40}


def rotate_ccw_screen(dx, dy, degrees):
    """CCW as actually seen on screen, for image coords (y grows downward,
    so this is the mirror of the textbook y-up CCW rotation matrix)."""
    t = np.radians(degrees)
    return dx * np.cos(t) + dy * np.sin(t), -dx * np.sin(t) + dy * np.cos(t)

PYMOL_CANDIDATES = [
    "/Applications/PyMOL.app/Contents/bin/pymol",
    "/usr/bin/pymol",
    "/opt/homebrew/bin/pymol",
]


def find_pymol():
    from shutil import which
    for c in [which("pymol")] + PYMOL_CANDIDATES:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    raise RuntimeError("Could not find a PyMOL executable; edit PYMOL_CANDIDATES.")


def load_font(size):
    for name in ("Arial Bold.ttf", "Arial.ttf"):
        for base in ("/System/Library/Fonts/Supplemental", "/Library/Fonts"):
            path = os.path.join(base, name)
            if os.path.isfile(path):
                return ImageFont.truetype(path, round(size))
    return ImageFont.load_default()


def find_color_bbox(img_arr, rgb, tol=20):
    target = np.array(rgb)
    dist = np.abs(img_arr - target).sum(axis=2)
    ys, xs = np.where(dist < tol)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max(), ys.max()


def text_box_at(cx, cy, tw, th):
    return (cx - tw / 2, cy - th / 2, cx + tw / 2, cy + th / 2)


def boxes_overlap(a, b, pad=6):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 + pad < bx0 or bx1 + pad < ax0 or ay1 + pad < by0 or by1 + pad < ay0)


def structure_overlap_fraction(structure_mask, box):
    x0, y0, x1, y1 = (max(0, int(box[0])), max(0, int(box[1])),
                       min(structure_mask.shape[1], int(box[2])), min(structure_mask.shape[0], int(box[3])))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    region = structure_mask[y0:y1, x0:x1]
    return region.mean() if region.size else 0.0


def place_label(cx, cy, tw, th, placed_boxes, structure_mask, max_r=180, ring_step=8,
                 n_angles=24, check_structure=True):
    """Try the original spot first; if blocked, spiral outward for the nearest clear spot.
    check_structure=False for a manually-positioned label: honor the exact requested
    spot unconditionally (a deliberate override), whatever's behind or next to it."""
    box = text_box_at(cx, cy, tw, th)
    structure_ok = (not check_structure) or structure_overlap_fraction(structure_mask, box) <= STRUCTURE_OVERLAP_MAX
    if not any(boxes_overlap(box, pb) for pb in placed_boxes) and structure_ok:
        return cx, cy, box
    if not check_structure:
        return cx, cy, box  # honor the manual position even if it collides with a label; don't drift it away
    r = ring_step
    while r <= max_r:
        for i in range(n_angles):
            angle = 2 * np.pi * i / n_angles
            ncx, ncy = cx + r * np.cos(angle), cy + r * np.sin(angle)
            box = text_box_at(ncx, ncy, tw, th)
            if any(boxes_overlap(box, pb) for pb in placed_boxes):
                continue
            if structure_overlap_fraction(structure_mask, box) > STRUCTURE_OVERLAP_MAX:
                continue
            return ncx, ncy, box
        r += ring_step
    return cx, cy, box  # give up, keep original


def main():
    session = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SESSION
    if not os.path.isfile(session):
        sys.exit(f"Missing session file: {session}")

    if os.path.isfile(OUT_SVG) and "inkscape:version" in open(OUT_SVG).read():
        sys.exit(
            f"{OUT_SVG} looks hand-edited in Inkscape (has inkscape:version "
            "metadata) -- refusing to overwrite it and destroy those edits.\n"
            "Move/rename it first if you really want to regenerate from "
            "scratch, or pass a different output by editing OUT_SVG."
        )

    pymol = find_pymol()
    clean_png = "/tmp/_asf_clean.png"
    ca_png = "/tmp/_asf_ca.png"
    label_png = "/tmp/_asf_label.png"
    positions_json = "/tmp/_asf_positions.json"
    wide_png = "/tmp/_asf_wide.png"
    wide_ca_png = "/tmp/_asf_wide_ca.png"

    subprocess.run(
        [pymol, "-cq", os.path.join(SCRIPTS, "_pymol_render_active_site_svg.py"),
         "--", session, clean_png, ca_png, label_png, positions_json, wide_png, wide_ca_png],
        check=True,
    )

    positions = json.load(open(positions_json))
    ca_arr = np.array(Image.open(ca_png).convert("RGB")).astype(int)
    label_arr = np.array(Image.open(label_png).convert("RGB")).astype(int)
    clean = Image.open(clean_png).convert("RGB")
    clean_arr = np.array(clean).astype(int)
    structure_mask = (np.abs(clean_arr - 255).sum(axis=2) > 15).astype(float)

    items = []
    for resi, info in positions.items():
        ca_box = find_color_bbox(ca_arr, info["ca_rgb"])
        lab_box = find_color_bbox(label_arr, info["lab_rgb"])
        if ca_box is None or lab_box is None:
            print(f"WARNING: couldn't locate {info['text']} (resi {resi}) in a render -- skipping")
            continue
        cax, cay = (ca_box[0] + ca_box[2]) / 2, (ca_box[1] + ca_box[3]) / 2
        lx0, ly0, lx1, ly1 = lab_box
        lcx, lcy = (lx0 + lx1) / 2, (ly0 + ly1) / 2

        deg = MANUAL_ROTATIONS.get(int(resi))
        manual = bool(deg)
        if deg:
            dx, dy = rotate_ccw_screen(lcx - cax, lcy - cay, deg)
            lcx, lcy = cax + dx, cay + dy

        font_size = (ly1 - ly0) / 0.72 * FONT_SCALE
        items.append({"text": info["text"], "ca": (cax, cay), "manual": manual,
                      "label_center": (lcx, lcy), "font_size": font_size})

    # Nudge any label that overlaps another label or sits mostly on the
    # structure, to the nearest clear spot -- preserving your placement
    # otherwise. Process labels closest-to-crowded-center first isn't
    # necessary; original render order is stable and fine.
    placed_boxes = []
    for it in items:
        font = load_font(it["font_size"])
        bbox = font.getbbox(it["text"])
        tw, th = (bbox[2] - bbox[0]) * 1.15, (bbox[3] - bbox[1]) * 1.3  # a little breathing room
        cx, cy = it["label_center"]
        fcx, fcy, box = place_label(cx, cy, tw, th, placed_boxes, structure_mask,
                                     check_structure=not it["manual"])
        placed_boxes.append(box)
        it["label_center"] = (fcx, fcy)

    # Crop tightly to the active site: bbox of residues + (possibly nudged)
    # labels, not just whitespace trimmed off the whole protein render.
    xs = [p for it in items for p in (it["ca"][0], it["label_center"][0])]
    ys = [p for it in items for p in (it["ca"][1], it["label_center"][1])]
    x0 = max(0, min(xs) - CROP_PAD)
    y0 = max(0, min(ys) - CROP_PAD)
    x1 = min(clean.width, max(xs) + CROP_PAD)
    y1 = min(clean.height, max(ys) + CROP_PAD)

    cropped = clean.crop((int(x0), int(y0), int(x1), int(y1)))
    cropped_path = "/tmp/_asf_cropped.png"
    cropped.save(cropped_path)
    W, H = cropped.size

    # Save the WIDE overview (whole protein, same session/camera, zoomed out
    # -- the "clean" render above is zoomed for the inset and cuts off most
    # of the protein, not usable as the full-structure overview) and the box
    # to draw on it, so assemble_panel_d_overview.py can reconstruct the
    # original two-part layout. The box comes from the wide CA markers'
    # actual positions at THIS wider zoom (a different camera distance than
    # the close-up render, so pixel coordinates aren't shared between them).
    overview_path = os.path.join(REPO, "Figure", "_panelD_overview_full.png")
    Image.open(wide_png).convert("RGB").save(overview_path)

    wide_ca_arr = np.array(Image.open(wide_ca_png).convert("RGB")).astype(int)
    wide_xs, wide_ys = [], []
    for resi, info in positions.items():
        box = find_color_bbox(wide_ca_arr, info["ca_rgb"])
        if box is None:
            continue
        wide_xs += [box[0], box[2]]
        wide_ys += [box[1], box[3]]
    wbox_pad = 40
    wx0 = float(max(0, min(wide_xs) - wbox_pad))
    wy0 = float(max(0, min(wide_ys) - wbox_pad))
    wx1 = float(max(wide_xs) + wbox_pad)
    wy1 = float(max(wide_ys) + wbox_pad)

    with open(os.path.join(REPO, "Figure", "_panelD_crop_box.json"), "w") as fh:
        json.dump({"x0": wx0, "y0": wy0, "x1": wx1, "y1": wy1,
                   "overview": os.path.relpath(overview_path, REPO)}, fh)  # repo-relative so the file is portable

    b64 = base64.b64encode(open(cropped_path, "rb").read()).decode("ascii")

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<image x="0" y="0" width="{W}" height="{H}" xlink:href="data:image/png;base64,{b64}"/>']

    for it in items:
        cax, cay = it["ca"][0] - x0, it["ca"][1] - y0
        lcx, lcy = it["label_center"][0] - x0, it["label_center"][1] - y0
        if (lcx - cax) ** 2 + (lcy - cay) ** 2 > 15 ** 2:
            svg.append(f'<line x1="{cax:.1f}" y1="{cay:.1f}" x2="{lcx:.1f}" y2="{lcy:.1f}" '
                       f'stroke="#505050" stroke-width="2"/>')
        svg.append(f'<circle cx="{cax:.1f}" cy="{cay:.1f}" r="4" fill="black"/>')
        svg.append(f'<text x="{lcx:.1f}" y="{lcy:.1f}" text-anchor="middle" '
                   f'dominant-baseline="central" font-family="Arial, sans-serif" '
                   f'font-weight="bold" font-size="{it["font_size"]:.1f}" fill="black">{it["text"]}</text>')
    svg.append("</svg>")

    os.makedirs(os.path.dirname(OUT_SVG), exist_ok=True)
    with open(OUT_SVG, "w") as fh:
        fh.write("\n".join(svg))
    cropped.save(OUT_PNG)  # label-free PNG, for convenience/consistency

    print(f"wrote {OUT_PNG} and {OUT_SVG} ({len(items)} labels)")


if __name__ == "__main__":
    main()
