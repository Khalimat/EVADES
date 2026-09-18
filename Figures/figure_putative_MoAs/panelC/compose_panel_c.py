"""
Composite the two PyMOL renders into the final Panel C image, matching the
original AcrIB4.png layout: two rows, each with a text label above the
Cas8-family chain (left) and the partner chain (right).

INPUTS: top_cas8_cas11.png, bottom_lscas8_acrib4.png (from build_panel_c.py).
OUTPUT: PanelC_final.png. Run: python3 compose_panel_c.py from this folder.
Uses macOS Times New Roman.
"""
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


def main():
    """Stack the two renders with text labels above each chain; save PanelC_final.png."""
    top = fit_width(load("top_cas8_cas11.png"), 1000)
    bottom = fit_width(load("bottom_lscas8_acrib4.png"), 1000)

    font = ImageFont.truetype(FONT_REG, 40)
    MARGIN = 20
    TOP_PAD = 90  # clears room for the panel-level "C" letter drawn over this image's top-left corner
    LABEL_H = 60
    GAP = 40

    W = 1000 + MARGIN * 2
    H = TOP_PAD + LABEL_H + top.height + GAP + LABEL_H + bottom.height + MARGIN

    canvas = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(canvas)

    y = TOP_PAD
    draw.text((MARGIN + 40, y), "Cas8 (8FCJ_I)", fill=BLACK, font=font)
    draw.text((MARGIN + 620, y), "Cas11 (8FCJ_L)", fill=BLACK, font=font)
    y += LABEL_H
    canvas.paste(top, (MARGIN, y))
    y += top.height + GAP

    draw.text((MARGIN + 130, y), "LsCas8", fill=BLACK, font=font)
    draw.text((MARGIN + 660, y), "AcrIB4", fill=BLACK, font=font)
    y += LABEL_H
    canvas.paste(bottom, (MARGIN, y))

    canvas.save("PanelC_final.png")
    print("saved PanelC_final.png", canvas.size)


if __name__ == "__main__":
    main()
