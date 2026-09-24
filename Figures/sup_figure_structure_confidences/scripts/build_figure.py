"""Assemble panels (pLDDT render + PAE per target, 2 columns x 4 rows) into one-page PDF."""
import os, json
from targets import TARGETS, RENDERS, ROOT

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from textwrap import wrap

OUT_PDF = os.path.join(ROOT, "output", "Supplementary_Figure_pLDDT_PAE.pdf")
LEGEND_PNG = os.path.join(RENDERS, "pLDDT_legend.png")

N = len(TARGETS)
COLS = 2
ROWS = (N + COLS - 1) // COLS  # 4 rows for 8 targets

PAGE_W = 420 * mm
PAGE_H = 446 * mm  # 460 mm minus the removed title strip
MARGIN = 14 * mm

LEGEND_H = 15 * mm
HEADER_GAP = 4 * mm

grid_top = PAGE_H - MARGIN - LEGEND_H - HEADER_GAP
grid_bottom = MARGIN + 6 * mm  # small footer space
grid_w = PAGE_W - 2 * MARGIN
grid_h = grid_top - grid_bottom

col_w = grid_w / COLS
row_h = grid_h / ROWS

IMG_H = row_h - 28 * mm   # reserve space for name + scores text
GAP = 4 * mm
IMG_W = (col_w - GAP - 8 * mm) / 2  # two images side by side within a block, small side padding

c = canvas.Canvas(OUT_PDF, pagesize=(PAGE_W, PAGE_H))

# Shared legend (once for all)
legend_reader = ImageReader(LEGEND_PNG)
lw, lh = legend_reader.getSize()
legend_draw_w = grid_w
legend_draw_h = legend_draw_w * lh / lw
if legend_draw_h > LEGEND_H:
    legend_draw_h = LEGEND_H
    legend_draw_w = legend_draw_h * lw / lh
legend_x = MARGIN + (grid_w - legend_draw_w) / 2
legend_y = PAGE_H - MARGIN - legend_draw_h
c.drawImage(legend_reader, legend_x, legend_y, width=legend_draw_w, height=legend_draw_h,
            preserveAspectRatio=True, mask='auto')

for idx, t in enumerate(TARGETS):
    row = idx // COLS
    col = idx % COLS

    block_x = MARGIN + col * col_w
    block_top = grid_top - row * row_h

    sc = json.load(open(t["summary"]))
    iptm = sc.get("iptm")
    ptm = sc.get("ptm")
    rscore = sc.get("ranking_score")

    # Name (wrapped, up to 2 lines)
    c.setFont("Helvetica-Bold", 14.25)
    name_lines = wrap(t["label"], 60)[:2]
    ty = block_top - 13.5
    for line in name_lines:
        c.drawString(block_x, ty, line)
        ty -= 15.75

    # Confidence scores line
    c.setFont("Helvetica", 12.75)
    c.drawString(block_x, ty, f"ranking score = {rscore:.2f}   ipTM = {iptm:.2f}   pTM = {ptm:.2f}")
    ty -= 12

    img_y = ty - IMG_H

    plddt_png = os.path.join(RENDERS, f"{t['name']}_pLDDT.png")
    pae_png = os.path.join(RENDERS, f"{t['name']}_PAE.png")

    ir1 = ImageReader(plddt_png)
    iw1, ih1 = ir1.getSize()
    scale1 = min(IMG_W / iw1, IMG_H / ih1)
    dw1, dh1 = iw1 * scale1, ih1 * scale1
    x1 = block_x
    y1 = img_y + (IMG_H - dh1)
    c.drawImage(ir1, x1, y1, width=dw1, height=dh1, preserveAspectRatio=True, mask='auto')

    ir2 = ImageReader(pae_png)
    iw2, ih2 = ir2.getSize()
    scale2 = min(IMG_W / iw2, IMG_H / ih2)
    dw2, dh2 = iw2 * scale2, ih2 * scale2
    x2 = block_x + IMG_W + GAP
    y2 = img_y + (IMG_H - dh2)
    c.drawImage(ir2, x2, y2, width=dw2, height=dh2, preserveAspectRatio=True, mask='auto')

c.showPage()
c.save()
print(f"wrote {OUT_PDF}")
