#!/usr/bin/env python3
"""Montage the per-substrate PyMOL panels (pymol/renders/parts/) into labelled supplementary figures.
A_<sub>.png = enzyme-DNA interface;  B_<sub>.png = same model coloured by AlphaFold pLDDT."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, "output", "parts")
OUT   = os.path.join(ROOT, "output")
PANEL = [("nicked", "nicked"), ("gap1nt", "1-nt gap"), ("gap2nt", "2-nt gap")]

# font sizes tuned for the ~4000 px wide, 300-dpi output
F_PANEL, F_ROW, F_LEG = 58, 46, 40
F_ROW_TAG = 48   # "A"/"B" row letters — 3x the nominal Supplementary Figure 1 size (16), i.e. its
                 # actual rendered size there (16 pt Plotly x scale 3)

LEGEND_A = [("#b3b3b3", "ORF55"),
            ("#f5deb3", "continuous strand"),
            ("#4a70b8", "upstream arm (3′-OH)"),
            ("#fa8072", "downstream arm (5′-P)"),
            ("#e03030", "nick / gap"),
            ("#ffd21f", "ATP"),
            ("dash",    "protein–DNA H-bond")]
LEGEND_B = [("#0D57D3", "very high  (pLDDT ≥ 90)"),
            ("#65CBF3", "high  (70–90)"),
            ("#FFDB13", "low  (50–70)"),
            ("#FF7D45", "very low  (< 50)"),
            ("#9E1CBD", "ATP")]

def font(sz, bold=False):
    cands = ([("/System/Library/Fonts/Helvetica.ttc", 1),
              ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0)] if bold else
             [("/System/Library/Fonts/Helvetica.ttc", 0),
              ("/System/Library/Fonts/Supplemental/Arial.ttf", 0)])
    for p, i in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz, index=i)
    return ImageFont.load_default()

def content_bbox(im):
    return ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()

def load_cropped(prefix):
    ims = [Image.open(f"{PARTS}/{prefix}_{t}.png").convert("RGB") for t, _ in PANEL]
    boxes = [b for b in (content_bbox(i) for i in ims) if b]
    if boxes:
        pad = 25
        l = max(0, min(b[0] for b in boxes) - pad)
        t = max(0, min(b[1] for b in boxes) - pad)
        r = min(ims[0].width,  max(b[2] for b in boxes) + pad)
        b = min(ims[0].height, max(b[3] for b in boxes) + pad)
        ims = [i.crop((l, t, r, b)) for i in ims]
    return ims

def _tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]

def draw_legend(d, W, y, cells, f, hf, sw=44, gap_in=15, item_gap=42,
                tight_gap=14, group_gap=100, group_pad=18):
    """Horizontal legend, centred on canvas width W, swatch tops at y.
    cells: (colour, label) | ("dash", label) | ("group", header, [(colour, label), ...])
    A group is drawn with a small centred header and tight internal spacing, set off
    from the neighbouring items by group_gap."""
    def item_w(lab):
        return sw + gap_in + _tw(d, lab, f)

    seg_w = []
    for c in cells:
        if c[0] == "group":
            inner = sum(item_w(l) for _, l in c[2]) + tight_gap * (len(c[2]) - 1)
            seg_w.append(max(inner + 2 * group_pad, _tw(d, c[1], hf)))
        else:
            seg_w.append(item_w(c[1]))
    total = sum(seg_w) + group_gap * (len(cells) - 1)
    x = (W - total) / 2

    for c, w in zip(cells, seg_w):
        if c[0] == "group":
            inner = sum(item_w(l) for _, l in c[2]) + tight_gap * (len(c[2]) - 1)
            d.text((x + w / 2, y - 12), c[1], font=hf, fill="#222", anchor="mb")
            xx = x + (w - inner) / 2
            for col, lab in c[2]:
                d.rectangle([xx, y, xx + sw, y + sw], fill=col, outline="#888", width=2)
                d.text((xx + sw + gap_in, y + sw / 2), lab, font=f, fill="#222", anchor="lm")
                xx += item_w(lab) + tight_gap
        else:
            col, lab = c
            if col == "dash":
                yc = y + sw // 2
                for s in range(0, sw, 14):
                    d.line([(x + s, yc), (x + s + 8, yc)], fill="#444", width=5)
            else:
                d.rectangle([x, y, x + sw, y + sw], fill=col, outline="#888", width=2)
            d.text((x + sw + gap_in, y + sw / 2), lab, font=f, fill="#222", anchor="lm")
        x += w + group_gap
    return x

def strip(prefix, outname, legend, sublabels=None):
    ims = load_cropped(prefix)
    h, gap = ims[0].height, 24
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    fP, fL, fS = font(F_PANEL), font(F_LEG), font(44)
    top, legh = 76, 250
    subh = 54 if sublabels else 0
    legend_gap = 72                       # space between the panel block (incl. sublabels) and the legend
    canvas = Image.new("RGB", (W, h + top + subh + legend_gap + legh), "white")
    d = ImageDraw.Draw(canvas)
    x = 0
    for (t, label), im in zip(PANEL, ims):
        canvas.paste(im, (x, top))
        d.text((x + im.width / 2, 10), label, font=fP, fill="black", anchor="mt")
        if sublabels:
            d.text((x + im.width / 2, top + h + 6), sublabels[t], font=fS, fill="#333", anchor="mt")
        x += im.width + gap
    ly = h + top + subh + legend_gap + 54            # + room for a group header above the swatches
    draw_legend(d, W, ly, legend, fL, font(F_LEG, bold=True))
    d.text((W / 2, ly + 86), "same view and scale in all panels", font=font(32), fill="#666", anchor="mt")
    canvas.save(f"{OUT}/{outname}", dpi=(300, 300))
    print("wrote", outname, canvas.size)

def combined(outname):
    fP, fR, fL = font(F_PANEL), font(F_ROW), font(F_LEG)
    fTag = font(F_ROW_TAG, bold=True)   # "A"/"B" letters: Supplementary Figure 1's nominal size, bold
    A = load_cropped("A"); B = load_cropped("B")
    colw, gap = A[0].width, 24
    W = colw * 3 + gap * 2
    header, rowlab, legh = 74, 58, 120
    pad_bottom = 20 + 71   # +0.6 cm at 300 dpi so the last legend row is not clipped
    Htot = header + rowlab + A[0].height + legh + rowlab + B[0].height + legh + pad_bottom
    canvas = Image.new("RGB", (W, Htot), "white")
    d = ImageDraw.Draw(canvas)
    for k, (_t, label) in enumerate(PANEL):
        d.text((k * (colw + gap) + colw / 2, 10), label, font=fP, fill="black", anchor="mt")
    y = header
    for tag, title, ims, legend in (
            ("A", "Enzyme–DNA interface (highest-confidence model per substrate)", A, LEGEND_A),
            ("B", "Same models, coloured by AlphaFold pLDDT", B, LEGEND_B)):
        gap_after_tag = d.textlength(tag + "   ", font=fR) - d.textlength(tag, font=fR)
        d.text((6, y + (F_ROW - F_ROW_TAG) / 2), tag, font=fTag, fill="black", anchor="lt")
        d.text((6 + d.textlength(tag, font=fTag) + gap_after_tag, y), title, font=fR,
               fill="black", anchor="lt")
        y += rowlab
        for k, im in enumerate(ims):
            canvas.paste(im, (k * (colw + gap), y))
        y += ims[0].height + 54
        draw_legend(d, W, y, legend, fL, font(F_LEG, bold=True))
        y += legh
    canvas.save(f"{OUT}/{outname}", dpi=(300, 300))
    print("wrote", outname, canvas.size)

strip("A", "SuppFig_interface_overview.png", LEGEND_A)
strip("B", "SuppFig_plddt.png", LEGEND_B)
combined("SuppFig_ORF55_DNA_structures.png")

CAPTION = (
    "Supplementary Figure 2. The lower co-folding confidence for a two-nucleotide gap is "
    "reflected in the modelled DNA, not in the enzyme-DNA interface. ORF55 engages all three "
    "substrates through an interface of the same type and size, and the protein is modelled at "
    "very high confidence throughout; what changes for the two-nucleotide gap is that the "
    "modelled DNA itself becomes markedly less certain. This mirrors the ipTM/pTM difference in "
    "Supplementary Figure 1 and is equally reproducible: every two-nucleotide-gap per-seed mean "
    "DNA pLDDT (72.6-85.8, n = 5 seeds) lies below that of every seed of every other substrate "
    "(pairwise P = 0.008, exact two-sided permutation test on the per-seed means, n = 5 per "
    "group).\n\n"
    "Panels show the highest-confidence AlphaFold 3 model of each substrate (nicked, one- and "
    "two-nucleotide-gapped 21-bp duplex + ATP), superposed on ORF55; same view and scale in all "
    "panels. (A) Enzyme-DNA interface. ORF55 grey (cartoon + transparent surface); the continuous "
    "(non-scissile) strand wheat; upstream cleaved arm (3'-OH at the junction) blue; downstream "
    "cleaved arm (5'-phosphate) salmon; the two nucleotides flanking the nick/gap red; ATP "
    "yellow; protein-DNA hydrogen bonds (heavy-atom N/O...N/O <= 3.5 A) dashed. A length-"
    "normalised quantification of the interface is given in Supplementary Table S1. (B) The same "
    "models coloured by AlphaFold pLDDT: dark blue, very high (>=90); light blue, high "
    "(70-90); yellow, low (50-70); orange, very low (<50); ATP purple. ORF55 stays very-high-"
    "confidence in every case (mean per-residue pLDDT >= 96). The modelled DNA is very-high-"
    "confidence for the nicked and one-nucleotide-gapped duplexes (mean DNA pLDDT 95.2 +/- 2.2 "
    "and 96.5 +/- 0.8 over 25 models; intact duplex 95.1 +/- 0.3) and drops from the very-high "
    "to the high band for the two-nucleotide gap (81.9 +/- 5.0), particularly along the duplex "
    "arms.")
open(os.path.join(OUT, "SuppFig_structures_caption.txt"), "w").write(CAPTION + "\n")
print("wrote SuppFig_structures_caption.txt")
