#!/usr/bin/env python3
"""Build Figure/NTase_D.png: the AF3 UTP-UTP-3xMg2+ model of YP_009091875.1
(Erinnyis ello granulovirus NTase), full-protein overview with the active
site boxed, plus a zoomed active-site view with contacting residues labelled.

Picks the best-ranked model automatically: across the 5 AF3-server seeds run
for the yp_009091875 / UTP+UTP+3xMg2+ condition (af3_results/with_utp_ctp/),
each with 5 diffusion samples, this takes the single (seed, sample) with the
highest AF3 ranking_score -- see find_best_model(). See
_pymol_render_panel_d.py for the active-site cutoff, coloring, and how the
overview is put in the same spatial orientation as panel A.

Depends on build_panel_a.py having been run at least once (needs its saved
Figure/_panelA_view.json).

Run: python3 scripts/build_panel_a.py   # first, if not already done
     python3 scripts/build_panel_d.py
"""
import glob
import json
import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "scripts")
OUT_PNG = os.path.join(REPO, "Figure", "NTase_D.png")
CONDITION = "ntase_yp_009091875_utp_utp_mg3"
SUPERPOSED_PDB = os.path.join(REPO, "structures", "ntase_YP_009091875.pdb")
VIEW_JSON = os.path.join(REPO, "Figure", "_panelA_view.json")

PYMOL_CANDIDATES = [
    "/Applications/PyMOL.app/Contents/bin/pymol",
    "/usr/bin/pymol",
    "/opt/homebrew/bin/pymol",
]

GRAY = (131, 131, 131)
MAGENTA = (243, 1, 243)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 211)
BG = (255, 255, 255)


def find_pymol():
    from shutil import which
    for c in [which("pymol")] + PYMOL_CANDIDATES:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    raise RuntimeError("Could not find a PyMOL executable; edit PYMOL_CANDIDATES.")


def find_best_model():
    """Highest ranking_score model.cif across all seeds for CONDITION."""
    best = None
    for conf_path in glob.glob(
        os.path.join(REPO, "af3_results", "**", f"{CONDITION}_seed*",
                     "*summary_confidences_*.json"),
        recursive=True,
    ):
        d = json.load(open(conf_path))
        score = d.get("ranking_score")
        if score is None:
            continue
        idx = conf_path.rsplit("_", 1)[-1].split(".")[0]
        cif_path = conf_path.replace("summary_confidences", "model").rsplit("_", 1)[0] + f"_{idx}.cif"
        if not os.path.isfile(cif_path):
            continue
        if best is None or score > best[0]:
            best = (score, cif_path)
    if best is None:
        sys.exit(f"No AF3 results found for condition {CONDITION!r} under af3_results/")
    return best


def load_font(size, bold=False):
    names = (
        ["Times New Roman Bold.ttf", "Times New Roman.ttf"] if bold
        else ["Times New Roman.ttf"]
    )
    for name in names:
        for base in ("/System/Library/Fonts/Supplemental", "/Library/Fonts"):
            path = os.path.join(base, name)
            if os.path.isfile(path):
                return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def trim(im, bg=BG, pad=40):
    diff = ImageChops.difference(im, Image.new("RGB", im.size, bg))
    bbox = diff.getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
    return im.crop((x0, y0, x1, y1))


def main():
    if not os.path.isfile(SUPERPOSED_PDB):
        sys.exit(f"Missing pre-superposed structure at {SUPERPOSED_PDB}")
    if not os.path.isfile(VIEW_JSON):
        sys.exit(
            f"Missing {VIEW_JSON} -- run build_panel_a.py first; panel D "
            "aligns onto its reference chain and reuses its saved camera."
        )

    score, cif_path = find_best_model()
    print(f"best model for {CONDITION}: {cif_path} (ranking_score={score:.3f})")

    pymol = find_pymol()
    overview_path = os.path.join(REPO, "Figure", "_panelD_overview.png")
    zoom_path = os.path.join(REPO, "Figure", "_panelD_zoom.png")
    subprocess.run(
        [pymol, "-cq", os.path.join(SCRIPTS, "_pymol_render_panel_d.py"),
         "--", cif_path, SUPERPOSED_PDB, VIEW_JSON, overview_path, zoom_path],
        check=True,
    )

    overview = trim(Image.open(overview_path).convert("RGB"))
    zoom = trim(Image.open(zoom_path).convert("RGB"))

    W = max(overview.width, zoom.width)
    overview = overview.resize((W, round(overview.height * W / overview.width)))
    zoom = zoom.resize((W, round(zoom.height * W / zoom.width)))

    legend_h = 200
    connector_h = 50
    H = overview.height + connector_h + zoom.height + legend_h
    canvas = Image.new("RGB", (W, H), BG)
    canvas.paste(overview, (0, 0))
    canvas.paste(zoom, (0, overview.height + connector_h))

    draw = ImageDraw.Draw(canvas)
    y0 = overview.height
    y1 = overview.height + connector_h
    draw.line([(W * 0.15, y0), (0, y1)], fill="black", width=2)
    draw.line([(W * 0.85, y0), (W, y1)], fill="black", width=2)
    draw.rectangle([0, y1, W, y1 + zoom.height], outline="black", width=2)

    ly = overview.height + connector_h + zoom.height + 25
    draw.text((10, ly), "Ligands", font=load_font(28, bold=True), fill="black")
    draw.text((W // 2 + 10, ly), "Active Site", font=load_font(28, bold=True), fill="black")

    dot_r = 16
    ly2 = ly + 45
    draw.ellipse([10, ly2, 10 + 2 * dot_r, ly2 + 2 * dot_r], fill=MAGENTA)
    draw.text((10 + 2 * dot_r + 12, ly2 - 4), "UTP", font=load_font(24), fill="black")
    draw.ellipse([10, ly2 + 45, 10 + 2 * dot_r, ly2 + 45 + 2 * dot_r], fill=YELLOW)
    draw.text((10 + 2 * dot_r + 12, ly2 + 41), "Mg2+", font=load_font(24), fill="black")

    draw.ellipse([W // 2 + 10, ly2, W // 2 + 10 + 2 * dot_r, ly2 + 2 * dot_r], fill=BLUE)
    draw.text((W // 2 + 10 + 2 * dot_r + 12, ly2 - 4), "Putative active site residues",
              font=load_font(24), fill="black")
    draw.text((W // 2 + 10 + 2 * dot_r + 12, ly2 + 28), "(YP_009091875)",
              font=load_font(24), fill="black")

    canvas.save(OUT_PNG)
    os.remove(overview_path)
    os.remove(zoom_path)
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
