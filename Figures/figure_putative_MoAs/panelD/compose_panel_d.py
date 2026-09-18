"""
Composite the four PyMOL renders into a single Figure 1, Panel D image,
mirroring the original layout (2x2 grid + zoom inset + shared electrostatic
colour bar). The sgRNA is drawn in green so it does not clash with the red<->blue
electrostatic-potential scale.

INPUTS: 01_overview_cas9_acr26_sgrna.png, 02_overview_with_targetDNA.png,
03_electrostatic_overview.png, 04_electrostatic_zoom.png (from build_panel_d.py).
OUTPUT: PanelD_final.png. Run: python3 compose_panel_d.py from this folder.
Uses macOS Times New Roman.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT_REG = f"{FONT_DIR}/Times New Roman.ttf"
FONT_BOLD = f"{FONT_DIR}/Times New Roman Bold.ttf"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (218, 40, 40)


def trim(im, pad=20, bg=WHITE):
    """Crop near-white margins from `im`, leaving `pad` pixels around the content."""
    gray = im.convert("L")
    bbox = gray.point(lambda p: 0 if p >= 250 else 255).getbbox()
    if bbox is None:
        return im
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(im.width, r + pad)
    b = min(im.height, b + pad)
    return im.crop((l, t, r, b))


def load(name):
    """Open an image as RGB and trim its white margins."""
    return trim(Image.open(name).convert("RGB"))


def fit_width(im, w):
    """Resize `im` to width `w`, keeping the aspect ratio."""
    h = int(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS)


def surface_bbox(im, pad=10):
    """Bounding box of the red<->blue electrostatic-potential surface in `im`
    (anything distinctly reddish or bluish, i.e. not neutral gray/green/white)."""
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


def legend_dot_row(draw, x, y, color, text, font, r=31, gap=18):
    # no outline - matches the plain filled-circle style used in panels A/B/C
    draw.ellipse((x, y, x + 2 * r, y + 2 * r), fill=color)
    draw.text((x + 2 * r + gap, y - 2), text, fill=BLACK, font=font)


def main():
    p1 = load("01_overview_cas9_acr26_sgrna.png")
    p2 = load("02_overview_with_targetDNA.png")
    p3 = load("03_electrostatic_overview.png")
    p4 = load("04_electrostatic_zoom.png")

    COL_W = 760
    p1 = fit_width(p1, COL_W)
    p2 = fit_width(p2, COL_W)
    p3 = fit_width(p3, COL_W)
    p4 = fit_width(p4, COL_W)

    font_reg = ImageFont.truetype(FONT_REG, 54)
    font_small = ImageFont.truetype(FONT_REG, 45)
    font_bold = ImageFont.truetype(FONT_BOLD, 63)

    LEGEND_H = 245  # grown to give the 3 legend rows real breathing room (no overlap with p2 below)
    GAP = 28
    MARGIN = 40

    # colour bar geometry (needed up front to size the canvas correctly)
    SCALE = 0.84  # +40% from the previous 0.6
    LENGTH_BOOST = 1.15  # bar length only +15%, height unchanged
    font_bar = ImageFont.truetype(FONT_REG, int(54 * SCALE))
    bar_w = int(COL_W * SCALE * LENGTH_BOOST)
    bar_h = int(78 * SCALE)

    x_left = MARGIN
    x_right = MARGIN * 2 + COL_W

    label_y = MARGIN + p3.height + GAP + p4.height + 12
    right_content_bottom = label_y + 62 + 45  # AcrIIA26 caption, two lines
    bar_title_h = int(54 * SCALE) + 10  # "Electrostatic potential" title above the bar
    bar_y0 = right_content_bottom + 20 + bar_title_h
    bar_bottom = bar_y0 + bar_h + int(54 * SCALE) + 8 + 10  # bar + number row + margin

    ty_bottom = MARGIN + p1.height + 12 + LEGEND_H + p2.height + 10 + 62 + 10  # target DNA row bottom

    W = MARGIN * 3 + COL_W * 2
    H = max(bar_bottom, ty_bottom) + MARGIN

    canvas = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(canvas)

    # --- left column: cartoon overview, then legend, then +DNA ---
    y = MARGIN
    canvas.paste(p1, (x_left, y))
    y += p1.height + 12

    legend_dot_row(draw, x_left, y, (0, 100, 0), "sgRNA", font_reg)
    legend_dot_row(draw, x_left, y + 85, (170, 170, 170), "SpyCas9", font_reg)
    legend_dot_row(draw, x_left, y + 170, (255, 235, 0), "AcrIIA26", font_reg)
    y += LEGEND_H

    canvas.paste(p2, (x_left, y))
    ty = y + p2.height + 10
    legend_dot_row(draw, x_left, ty, (242, 115, 0), "target DNA", font_reg)

    # --- right column: electrostatic overview + red box, then zoom inset ---
    y = MARGIN
    canvas.paste(p3, (x_right, y))

    # box around the actual AcrIIA26 electrostatic surface in p3 (detected from
    # its red/blue coloring, not a hardcoded guess -> stays correct across
    # camera/complex changes)
    sb = surface_bbox(p3)
    bx0 = x_right + sb[0]
    by0 = y + sb[1]
    bx1 = x_right + sb[2]
    by1 = y + sb[3]
    draw.rectangle((bx0, by0, bx1, by1), outline=RED, width=4)

    y2 = y + p3.height + GAP
    canvas.paste(p4, (x_right, y2))
    draw.rectangle((x_right, y2, x_right + p4.width, y2 + p4.height), outline=RED, width=4)

    # connector lines from box corners to inset corners
    draw.line((bx0, by1, x_right, y2), fill=RED, width=3)
    draw.line((bx1, by1, x_right + p4.width, y2), fill=RED, width=3)

    draw.text((x_right, label_y), "AcrIIA26", fill=BLACK, font=font_reg)
    draw.text((x_right, label_y + 62), "(coloured based on electrostatic potential)", fill=BLACK, font=font_small)

    # --- shared electrostatic potential colour bar: shrunk 40%, placed right
    # under the AcrIIA26 caption/zoom inset (the structure it actually describes)
    # instead of spanning the full width down in the left column. Title goes
    # above the bar (not squeezed onto the same line as -5.000/5.000, which
    # doesn't fit at this narrower width) ---
    bar_x0 = x_right
    label = "Electrostatic potential"
    lw = draw.textlength(label, font=font_bar)
    draw.text((bar_x0 + (bar_w - lw) / 2, bar_y0 - bar_title_h), label, fill=BLACK, font=font_bar)

    grad = Image.new("RGB", (bar_w, bar_h))
    gd = ImageDraw.Draw(grad)
    red = (222, 25, 25)
    white = (255, 255, 255)
    blue = (25, 25, 222)
    for i in range(bar_w):
        t = i / (bar_w - 1)
        if t < 0.5:
            u = t / 0.5
            c = tuple(int(red[k] + (white[k] - red[k]) * u) for k in range(3))
        else:
            u = (t - 0.5) / 0.5
            c = tuple(int(white[k] + (blue[k] - white[k]) * u) for k in range(3))
        gd.line((i, 0, i, bar_h), fill=c)
    canvas.paste(grad, (bar_x0, bar_y0))
    draw.rectangle((bar_x0, bar_y0, bar_x0 + bar_w, bar_y0 + bar_h), outline=BLACK, width=2)
    draw.text((bar_x0, bar_y0 + bar_h + 8), "-5.000", fill=BLACK, font=font_bar)
    tw = draw.textlength("5.000", font=font_bar)
    draw.text((bar_x0 + bar_w - tw, bar_y0 + bar_h + 8), "5.000", fill=BLACK, font=font_bar)

    canvas.save("PanelD_final.png")
    print("saved PanelD_final.png", canvas.size)


if __name__ == "__main__":
    main()
