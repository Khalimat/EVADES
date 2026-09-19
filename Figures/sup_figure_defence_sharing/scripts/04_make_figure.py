"""Merge panel A (network, vector) and panel B (complexes) into one figure -> Defence_sharing_figure.svg / .png.
Run scripts 01-03 first. Run from the project root."""
import base64, io, re, subprocess
import numpy as np
from PIL import Image, ImageOps

def trimmed_png_b64(path, pad=30):
    im = Image.open(path).convert("RGBA")                       # PyMOL PNGs have an alpha channel: flatten onto white
    im = Image.alpha_composite(Image.new("RGBA", im.size, "white"), im).convert("RGB"); a = np.asarray(im)
    ys, xs = np.where((a < 248).any(-1))
    im = ImageOps.expand(im, pad, "white")                        # pad first so the crop box never leaves the image
    im = im.crop((xs.min(), ys.min(), xs.max() + 2 * pad, ys.max() + 2 * pad))
    buf = io.BytesIO(); im.save(buf, "PNG"); return base64.b64encode(buf.getvalue()).decode(), im.size

W, A_H = 3300, 2600
net = open("panels/panelA_network.svg").read()
inner = re.search(r"<svg[^>]*>(.*)</svg>", net, re.S).group(1)             # network drawing, own coordinate system
B_TOP, ROW_H = A_H + 60, 1250
parts = [f'<g id="panelA"><svg x="0" y="0" width="{W}" height="{A_H}" viewBox="-1300 -1300 3300 2600">{inner}</svg></g>',
         '<g id="panelB" font-family="Times New Roman, Times, serif">']
for i, (name, title) in enumerate((("drmMI", "Ocr : drmMI"), ("gp28", "Ocr : gp28"))):
    b64, (w, h) = trimmed_png_b64(f"panels/panelB_{name}_complex.png")
    box_w, box_x = 1560, 60 + i * 1650
    s = min(box_w / w, ROW_H / h); iw, ih = w * s, h * s
    parts.append(f'<text x="{box_x + box_w / 2}" y="{B_TOP + 70}" font-size="70" text-anchor="middle">{title}</text>')
    parts.append(f'<image x="{box_x + (box_w - iw) / 2}" y="{B_TOP + 110 + (ROW_H - ih) / 2}" width="{iw}" height="{ih}" href="data:image/png;base64,{b64}"/>')
leg_y = B_TOP + 110 + ROW_H + 90
for x, c, t in ((900, "#b887de", "Defence protein"), (1700, "#b3b3b3", "Ocr")):
    parts.append(f'<circle cx="{x}" cy="{leg_y}" r="34" fill="{c}"/><text x="{x + 60}" y="{leg_y + 22}" font-size="66">{t}</text>')
parts.append("</g>")
H = leg_y + 120
parts.append(f'<g font-family="Times New Roman, Times, serif" font-weight="bold" font-size="120"><text x="30" y="120">A</text><text x="30" y="{B_TOP + 110}">B</text></g>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="white"/>' + "".join(parts) + "</svg>")
open("Defence_sharing_figure.svg", "w").write(svg)
open("_fig.html", "w").write(f'<body style="margin:0"><img src="Defence_sharing_figure.svg" style="width:{W}px;height:{H}px;display:block">')
subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--headless=new", "--hide-scrollbars", f"--window-size={W},{H}",
                "--force-device-scale-factor=1", "--screenshot=Defence_sharing_figure.png", "file://" + __import__("os").path.abspath("_fig.html")],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import os; os.remove("_fig.html")
print("saved Defence_sharing_figure.svg / .png", W, H)
