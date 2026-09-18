"""
Composite the Panel A render with its colour-code legend (PaCas8c grey dot,
PAM binding site yellow dot) and the AcrIC5 electrostatic-potential caption,
matching the style of panels C/D.

INPUT: PanelA_render.png (from build_panel_a.py). OUTPUT: PanelA_final.png.
Run: python3 compose_panel_a.py (from this folder). Uses macOS Times New Roman.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT_REG = f"{FONT_DIR}/Times New Roman.ttf"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def trim(im, pad=20):
    """Crop near-white margins from `im`, leaving `pad` pixels around the content."""
    gray = im.convert("L")
    bbox = gray.point(lambda p: 0 if p >= 250 else 255).getbbox()
    if bbox is None:
        return im
    l, t, r, b = bbox
    l = max(0, l - pad); t = max(0, t - pad)
    r = min(im.width, r + pad); b = min(im.height, b + pad)
    return im.crop((l, t, r, b))


def surface_bbox(im, pad=10):
    """Bounding box of the red<->blue electrostatic-potential surface (AcrIC5)
    in `im` - anything distinctly reddish or bluish, not neutral grey/white."""
    arr = np.array(im).astype(int)
    R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]
    reddish = (R - G > 12) & (R - B > 12)
    bluish = (B - R > 12) & (B - G > 12)
    mask = reddish | bluish
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    l, r = max(0, xs.min() - pad), min(im.width, xs.max() + pad)
    t, b = max(0, ys.min() - pad), min(im.height, ys.max() + pad)
    return (l, t, r, b)


def legend_dot_row(draw, x, y, color, text, font, r=27, gap=18):
    """Draw a colour dot of radius `r` at (x, y) followed by its label."""
    draw.ellipse((x, y, x + 2 * r, y + 2 * r), fill=color)
    draw.text((x + 2 * r + gap, y - 2), text, fill=BLACK, font=font)


def main():
    """Trim and resize the render, add the AcrIC5 caption and the legend, save PanelA_final.png."""
    render = trim(Image.open("PanelA_render.png").convert("RGB"))
    render = render.resize((1400, int(render.height * 1400 / render.width)), Image.LANCZOS)

    # r=27 / font=58 here -> ~30px dots in the Figure 1 composite after being
    # scaled down to COL_W=800 (matches panels B/C/D's legend dot size)
    font = ImageFont.truetype(FONT_REG, 58)

    MARGIN = 20
    TOP_PAD = 90  # clears room for the panel-level "A" letter drawn over this image's top-left corner
    CAPTION_H = 60  # space below the render for the AcrIC5 caption
    LEGEND_H = 150

    W = render.width + MARGIN * 2
    H = TOP_PAD + render.height + CAPTION_H + LEGEND_H + MARGIN

    canvas = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(canvas)

    render_y = TOP_PAD
    canvas.paste(render, (MARGIN, render_y))

    # caption directly below the AcrIC5 electrostatic surface (detected by
    # colour, not a fixed offset) - stays correct regardless of orientation
    sb = surface_bbox(render)
    font_small = ImageFont.truetype(FONT_REG, 47)
    cap1, cap2 = "AcrIC5", "(coloured based on electrostatic potential)"
    w1 = draw.textlength(cap1, font=font)
    w2 = draw.textlength(cap2, font=font_small)
    blob_cx = MARGIN + ((sb[0] + sb[2]) / 2 if sb is not None else render.width / 2)
    cap_top = render_y + render.height  # always below the whole render - never overlaps structure
    x1 = min(max(blob_cx - w1 / 2, MARGIN), W - MARGIN - w1)
    x2 = min(max(blob_cx - w2 / 2, MARGIN), W - MARGIN - w2)
    draw.text((x1, cap_top), cap1, fill=BLACK, font=font)
    draw.text((x2, cap_top + 46), cap2, fill=BLACK, font=font_small)

    y = render_y + render.height + CAPTION_H
    legend_dot_row(draw, MARGIN, y, (170, 170, 170), "PaCas8c", font)
    legend_dot_row(draw, MARGIN, y + 78, (255, 255, 0), "PAM binding site", font)

    canvas.save("PanelA_final.png")
    print("saved PanelA_final.png", canvas.size)


if __name__ == "__main__":
    main()
