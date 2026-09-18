"""
Composite the Panel B render with its domain colour-code legend and the
domain-architecture bar (with real interface-residue ticks), matching the
style of the original figure.

INPUTS: PanelB_render.png (build_panel_b.py), PanelB_domain_bar.png (build_domain_bar.py).
OUTPUT: PanelB_final.png. Run: python3 compose_panel_b.py from this folder.
Uses macOS Times New Roman.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT_REG = f"{FONT_DIR}/Times New Roman.ttf"
FONT_BOLD = f"{FONT_DIR}/Times New Roman Bold.ttf"

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


def gray_bbox(im, pad=10):
    """Bounding box of the grey70 AcrIC3 chain in `im` (neutral mid-grey,
    not the white background or black cartoon outlines)."""
    arr = np.array(im).astype(int)
    R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]
    gray = (abs(R - G) < 8) & (abs(G - B) < 8) & (R > 140) & (R < 215)
    ys, xs = np.where(gray)
    if len(xs) == 0:
        return None
    l, r = max(0, xs.min() - pad), min(im.width, xs.max() + pad)
    t, b = max(0, ys.min() - pad), min(im.height, ys.max() + pad)
    return (l, t, r, b)


def legend_dot_row(draw, x, y, color, text, font, r=30, gap=20):
    """Draw a colour dot of radius `r` at (x, y) followed by its label."""
    draw.ellipse((x, y, x + 2 * r, y + 2 * r), fill=color)
    draw.text((x + 2 * r + gap, y - 2), text, fill=BLACK, font=font)


def fit_width(im, w):
    """Resize `im` to width `w`, keeping the aspect ratio."""
    h = int(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS)


def main():
    """Lay out legend (left), structure render (right) and domain bar (bottom); save PanelB_final.png."""
    render = trim(Image.open("PanelB_render.png").convert("RGB"))
    render = fit_width(render, 1300)

    bar = Image.open("PanelB_domain_bar.png").convert("RGBA")
    bg = Image.new("RGB", bar.size, WHITE)
    bg.paste(bar, mask=bar.split()[3])
    bar = fit_width(bg, 1300)  # longer bar, matches render width

    # r=30 / font=60 here -> ~30px dots in the Figure 1 composite after being
    # scaled down to COL_W=800 (matches panels A/C/D's legend dot size)
    font = ImageFont.truetype(FONT_REG, 60)
    font_title = ImageFont.truetype(FONT_REG, 60)

    MARGIN = 20
    LEGEND_W = 300  # pulled closer to the complex (was 480, then 420)
    LEGEND_ROW_H = 90

    legend_entries = [
        ((255, 255, 0), "HD"),
        ((0, 255, 255), "RecA1"),
        ((34, 139, 34), "RecA2"),
        ((255, 182, 193), "Linker"),
        ((255, 0, 255), "CTD"),
    ]

    font_caption = ImageFont.truetype(FONT_REG, 44)  # sized for the render/bar, not the legend (34 * 1.3)

    TOP_PAD = 210  # clears room for the panel-level "B" letter drawn over this image's top-left corner
    # (PanelB_final.png is scaled down ~2.3x when fit to COL_W in Figure 1, so
    # the native pad here needs to be proportionally larger than in panel C)

    by = TOP_PAD + render.height + 20  # y where the domain-bar caption starts
    bar_y = by + 58                     # y where the bar image itself starts (caption is now larger)

    W = LEGEND_W + render.width + MARGIN * 3
    H = bar_y + bar.height + MARGIN * 2

    canvas = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(canvas)

    # left column: legend
    x = MARGIN
    y = TOP_PAD
    draw.text((x, y), "PaCas3", fill=BLACK, font=font_title)
    draw.text((x, y + 64), "domains", fill=BLACK, font=font_title)
    y += 144
    for color, text in legend_entries:
        legend_dot_row(draw, x, y, color, text, font)
        y += LEGEND_ROW_H
    # AcrIC3 is not a PaCas3 domain - kept out of this legend, labelled
    # directly above the structure instead (larger font, see below)

    # right: structure render
    rx = MARGIN * 2 + LEGEND_W
    canvas.paste(render, (rx, TOP_PAD))

    font_acr_label = ImageFont.truetype(FONT_REG, 60)  # same size as the legend text
    gb = gray_bbox(render)
    if gb is not None:
        acr_label = "AcrIC3"
        acr_r = 30
        acr_gap = 20
        alw = acr_r * 2 + acr_gap + draw.textlength(acr_label, font=font_acr_label)
        acx = rx + (gb[0] + gb[2]) / 2 - alw / 2
        acx = min(max(acx, rx), rx + render.width - alw)
        acy = TOP_PAD + gb[1] - 70  # just above the grey chain's top edge
        legend_dot_row(draw, acx, max(acy, 0), (170, 170, 170), acr_label, font_acr_label, r=acr_r, gap=acr_gap)

    # bottom: domain architecture bar, spanning most of the width
    draw.text((rx, by), "PaCas3 (UEM35119.1) domain architecture", fill=BLACK, font=font_caption)
    canvas.paste(bar, (rx, bar_y))

    canvas.save("PanelB_final.png")
    print("saved PanelB_final.png", canvas.size)


if __name__ == "__main__":
    main()
