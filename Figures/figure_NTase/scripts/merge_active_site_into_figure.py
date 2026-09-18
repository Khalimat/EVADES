#!/usr/bin/env python3
"""Replace panel D's structure content (group "g29786": the old
overview+box+zoomed-inset composition) in Figure/NTase_figure.svg with the
current Figure/active_site_labeled.svg (whatever you've hand-edited in
Inkscape), embedded as a raster image sized to fit the same panel-D
bounding box. The panel D legend group ("g45385": Ligands/Active Site key)
is left untouched.

Then re-exports Figure/NTase_figure.png at the same 250dpi as the rest of
the figure.

Run: python3 scripts/merge_active_site_into_figure.py
"""
import base64
import os
import subprocess
import shutil
import sys

from lxml import etree

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURE_DIR = os.path.join(REPO, "Figure")
MASTER_SVG = os.path.join(FIGURE_DIR, "NTase_figure.svg")
MASTER_PNG = os.path.join(FIGURE_DIR, "NTase_figure.png")
ACTIVE_SITE_SVG = os.path.join(FIGURE_DIR, "active_site_labeled.svg")
PANEL_D_GROUP_ID = "g29786"
EXPORT_DPI = 250

INKSCAPE = "/Applications/Inkscape.app/Contents/MacOS/inkscape"
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"


def main():
    # Either pass a ready-made raster (e.g. Figure/panelD_full.png, the full
    # overview+box+inset composite from assemble_panel_d_overview.py), or
    # omit it to just rasterize active_site_labeled.svg directly (inset only).
    source_png = sys.argv[1] if len(sys.argv) > 1 else None

    from PIL import Image
    if source_png:
        if not os.path.isfile(source_png):
            raise SystemExit(f"Missing {source_png}")
        raster_path = source_png
    else:
        if not os.path.isfile(ACTIVE_SITE_SVG):
            raise SystemExit(f"Missing {ACTIVE_SITE_SVG}")
        raster_path = "/tmp/_merge_active_site.png"
        subprocess.run(
            [INKSCAPE, "--export-type=png", "--export-dpi=300",
             f"--export-filename={raster_path}", ACTIVE_SITE_SVG],
            check=True,
        )
    img_w_px, img_h_px = Image.open(raster_path).size
    aspect = img_w_px / img_h_px

    # 2. Panel D's current bounding box in the master SVG (mm == user units
    # here, since the doc is declared in mm with a matching viewBox).
    out = subprocess.run(
        [INKSCAPE, f"--query-id={PANEL_D_GROUP_ID}",
         "--query-x", "--query-y", "--query-width", "--query-height", MASTER_SVG],
        capture_output=True, text=True, check=True,
    ).stdout.strip().splitlines()
    x_px, y_px, w_px, h_px = (float(v) for v in out)
    px_to_mm = 25.4 / 96.0
    bbox_x, bbox_y, bbox_w, bbox_h = (x_px * px_to_mm, y_px * px_to_mm,
                                       w_px * px_to_mm, h_px * px_to_mm)
    print(f"Panel D bbox (mm): x={bbox_x:.2f} y={bbox_y:.2f} w={bbox_w:.2f} h={bbox_h:.2f}")

    # 3. Contain within the old bbox on WHICHEVER axis is tighter (this
    # composite can be much taller/narrower than the inset alone was), so it
    # never overflows into the legend below or the panel to the right;
    # center on the other axis.
    bbox_aspect = bbox_w / bbox_h
    if aspect > bbox_aspect:  # wider than the box -> fit by width
        new_w = bbox_w
        new_h = new_w / aspect
    else:  # taller than the box -> fit by height
        new_h = bbox_h
        new_w = new_h * aspect
    new_x = bbox_x + (bbox_w - new_w) / 2.0
    new_y = bbox_y + (bbox_h - new_h) / 2.0
    print(f"Placing at (mm): x={new_x:.2f} y={new_y:.2f} w={new_w:.2f} h={new_h:.2f}")

    with open(raster_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    tree = etree.parse(MASTER_SVG)
    root = tree.getroot()
    ns = {"svg": SVG_NS}
    old_group = root.find(f'.//svg:g[@id="{PANEL_D_GROUP_ID}"]', ns)
    if old_group is None:
        raise SystemExit(f"Could not find group id={PANEL_D_GROUP_ID!r} in {MASTER_SVG}")

    new_image = etree.Element(f"{{{SVG_NS}}}image")
    new_image.set("id", "panelD_active_site")
    new_image.set("x", repr(new_x))
    new_image.set("y", repr(new_y))
    new_image.set("width", repr(new_w))
    new_image.set("height", repr(new_h))
    new_image.set("preserveAspectRatio", "none")
    new_image.set(f"{{{XLINK_NS}}}href", f"data:image/png;base64,{b64}")

    parent = old_group.getparent()
    parent.replace(old_group, new_image)

    svg_backup = MASTER_SVG + ".bak3"
    if not os.path.exists(svg_backup):
        shutil.copy2(MASTER_SVG, svg_backup)
    tree.write(MASTER_SVG, xml_declaration=True, encoding="UTF-8", standalone=False)
    print(f"Updated {MASTER_SVG} (backed up to {svg_backup})")

    png_backup = MASTER_PNG + ".bak3"
    if os.path.isfile(MASTER_PNG) and not os.path.exists(png_backup):
        shutil.copy2(MASTER_PNG, png_backup)

    subprocess.run(
        [INKSCAPE, f"--export-dpi={EXPORT_DPI}", "--export-type=png",
         f"--export-filename={MASTER_PNG}", MASTER_SVG],
        check=True,
    )
    w, h = Image.open(MASTER_PNG).size
    print(f"Wrote {MASTER_PNG} ({w}x{h}px @ {EXPORT_DPI}dpi)")


if __name__ == "__main__":
    main()
