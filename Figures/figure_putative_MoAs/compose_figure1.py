"""
Assemble the full Figure 1 (panels A-D) from the individual panel images:
  A = AcrIC5.png        (top-left)
  B = AcrIC3.png        (top-right)
  C = AcrIB4.png        (bottom-left)
  D = panelD/PanelD_final.png  (bottom-right; sgRNA drawn in green)

INPUTS (relative to this folder): panelA/PanelA_final.png, panelB/PanelB_final.png,
panelC/PanelC_final.png, panelD/PanelD_final.png  (each made by that panel's
compose_panel_*.py). OUTPUT: Figure1_final.png. Run: python3 compose_figure1.py

Layout follows the original MoA.svg structure: two columns (A+C on the left,
B+D on the right), each column scaled to a common width. Panel D is taller
than the others (it now carries three sub-rows + legend + colour bar), so the
right column is taller than the left - that's expected, not a bug.
"""
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT_BOLD = f"{FONT_DIR}/Times New Roman Bold.ttf"
FONT_REG = f"{FONT_DIR}/Times New Roman.ttf"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def load(name):
    """Open an image file as RGB."""
    return Image.open(name).convert("RGB")


def fit_width(im, w):
    """Resize `im` to width `w`, keeping the aspect ratio."""
    h = int(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS)


def fit_height(im, h):
    """Resize `im` to height `h`, keeping the aspect ratio."""
    w = int(im.width * h / im.height)
    return im.resize((w, h), Image.LANCZOS)


def legend_dot_row(draw, x, y, color, text, font, r=20, gap=14):
    """Draw one legend entry: a filled dot of radius `r` at (x, y) followed by `text`."""
    draw.ellipse((x, y, x + 2 * r, y + 2 * r), fill=color)
    draw.text((x + 2 * r + gap, y - 2), text, fill=BLACK, font=font)


def add_legend_strip(im, entries, height=90, r=20):
    """Return a copy of `im` with a white strip appended below it, carrying a
    dot+label colour-code legend (matches the style used in panels A/B/D).
    Entries are laid out side by side in one row."""
    canvas = Image.new("RGB", (im.width, im.height + height), WHITE)
    canvas.paste(im, (0, 0))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(FONT_REG, 34)
    y = im.height + (height - 2 * r) // 2
    x = 10
    for color, text in entries:
        legend_dot_row(draw, x, y, color, text, font, r=r)
        tw = draw.textlength(text, font=font)
        x += 2 * r + 14 + tw + 60  # gap before next entry
    return canvas


def main():
    """Load the four panels, scale them into two columns (A+C left, B+D right),
    add the panel-C legend and the A-D letters, and save Figure1_final.png."""
    a = load("panelA/PanelA_final.png")
    b = load("panelB/PanelB_final.png")
    c = load("panelC/PanelC_final.png")
    d = load("panelD/PanelD_final.png")

    COL_W = 1100  # bumped up for higher final resolution (was 800) - helps fine detail like panel B's domain bar
    a = fit_width(a, COL_W)
    b = fit_width(b, COL_W)
    c = fit_width(c, COL_W)  # back to baseline (was +20%, now matches A/B)

    # colour-code legend for panel C: light violet for the Cas8 homologs,
    # grey70 for the accessory/inhibitor chain (matches SpyCas9 grey in Panel D).
    # r=15 -> ~30px dots in the final composite, matching the size of the
    # dots already embedded in panels A/B/D.
    c = add_legend_strip(c, [
        ((184, 135, 222), "Cas8 / LsCas8"),
        ((179, 179, 179), "Cas11 / AcrIB4"),
    ], r=15, height=55)

    left_col_w = max(COL_W, c.width)  # C may now be wider than COL_W

    MARGIN = 50
    GAP_LEFT = 130    # more air between A and C
    GAP_RIGHT = 20    # tighter between B and D
    LABEL_FONT_SIZE = 51  # -20% from 64
    LABEL_PAD = 14
    font_label = ImageFont.truetype(FONT_BOLD, LABEL_FONT_SIZE)

    left_col_h = a.height + GAP_LEFT + c.height

    # scale D (independently of COL_W) so the right column's total height
    # matches the left column, instead of D dominating with its own width
    d_target_h = left_col_h - b.height - GAP_RIGHT
    d = fit_height(d, int(d_target_h * 1.5 * 0.9 * 0.85 * 0.8))  # 1.5x, -10%, -15%, then -20%

    right_col_w = max(COL_W, d.width)  # D may now be wider than COL_W

    # C and D start at the same Y (aligned to D's row, under B + GAP_RIGHT)
    row2_y = b.height + GAP_RIGHT
    left_col_h = row2_y + c.height
    right_col_h = row2_y + d.height
    col_h = max(left_col_h, right_col_h)

    W = MARGIN * 3 + left_col_w + right_col_w
    H = MARGIN * 2 + col_h

    canvas = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(canvas)

    x_left = MARGIN
    x_right = MARGIN * 2 + left_col_w
    y0 = MARGIN

    def place(im, x, y, label):
        canvas.paste(im, (x, y))
        draw.text((x + LABEL_PAD, y + LABEL_PAD), label, fill=BLACK, font=font_label)

    place(a, x_left, y0, "A")
    # centre C horizontally within the (possibly wider) left column
    c_x = x_left + (left_col_w - c.width) // 2
    place(c, c_x, y0 + row2_y, "C")

    place(b, x_right, y0, "B")
    # centre D horizontally within the (possibly wider) right column
    d_x = x_right + (right_col_w - d.width) // 2
    place(d, d_x, y0 + row2_y, "D")

    canvas.save("Figure1_final.png")
    print("saved Figure1_final.png", canvas.size)


if __name__ == "__main__":
    main()
