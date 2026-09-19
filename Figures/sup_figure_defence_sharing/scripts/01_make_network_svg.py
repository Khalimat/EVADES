"""Panel A: defence-protein sharing network as SVG (circular layout). Run from the project root."""
import pandas as pd, networkx as nx, numpy as np
import matplotlib
from collections import defaultdict
from xml.sax.saxutils import escape

df = pd.read_csv("data/similarity.csv")

shared_color_categories = {
    "BREX": ["BREX_I", "BREX_I,BREX_II,BREX_V", "BREX_II,BREX_VI", "BREX_V,BREX_II"],
    "PARIS": ["PARIS_I", "PARIS_I,PARIS_II", "PARIS_II"],
    "Retron_I_A": ["Retron_I_A (Ec78)", "Retron_I_A (Vc95, Ec83 and Ec78)"],
    "CRISPR": ["type I-E CRISPR-Cas", "type I-F CRISPR-Cas"],
}
unique_def = set(df["defence_1"]) | set(df["defence_2"])
category_mapping = {}
for d in unique_def:
    category_mapping[d] = next((g for g, m in shared_color_categories.items() if d in m), d)
unique_categories = sorted(set(category_mapping.values()))
cmap = matplotlib.colormaps["tab20"].resampled(len(unique_categories))
category_colors = {c: matplotlib.colors.to_hex(cmap(i)) for i, c in enumerate(unique_categories)}
colors = {d: category_colors[category_mapping[d]] for d in unique_def}

G = nx.Graph()
inhibitors = defaultdict(set)
for _, r in df.iterrows():
    p1, d1, i1, p2, d2, i2 = (r[k] for k in ["protein_name_1", "defence_1", "ADP(s)_1",
                                             "protein_name_2", "defence_2", "ADP(s)_2"])
    G.add_node(p1, defence=d1); G.add_node(p2, defence=d2); G.add_edge(p1, p2)
    if i1 != "_" and i1.lower() != "none": inhibitors[i1].add(p1)
    if i2 != "_" and i2.lower() != "none": inhibitors[i2].add(p2)

pos = {n: (x * 1000, y * 1000) for n, (x, y) in nx.circular_layout(G).items()}  # y down, as in vis.js
R, FS, TRI = 20, 36, 30      # FS = label font size (36 = 1.5 x 24)
edges, nodes, labels = [], [], []

for u, v in G.edges():
    edges.append(f'<line x1="{pos[u][0]:.1f}" y1="{pos[u][1]:.1f}" x2="{pos[v][0]:.1f}" y2="{pos[v][1]:.1f}"/>')

def label(x, y, t):
    labels.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle">{escape(t)}</text>')

for n, (x, y) in pos.items():
    nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{R}" fill="{colors[G.nodes[n]["defence"]]}"><title>{escape(G.nodes[n]["defence"])}</title></circle>')
    label(x, y + R + FS, n)

for inh, targets in inhibitors.items():
    for t in targets:
        tx, ty = pos[t]
        ix, iy = tx * 1.15, ty * 1.15
        edges.append(f'<line x1="{ix:.1f}" y1="{iy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}"/>')
        pts = f"{ix:.1f},{iy - TRI:.1f} {ix - TRI:.1f},{iy + TRI * .7:.1f} {ix + TRI:.1f},{iy + TRI * .7:.1f}"
        nodes.append(f'<polygon points="{pts}" fill="red" stroke="#b00" stroke-width="1.5"><title>Inhibitor: {escape(inh)}</title></polygon>')
        label(ix, iy + TRI * .7 + FS, inh)

# legend (right of the network); sizes are 1.5 x the original
lx, ly, STEP = 1400, -1000, 78
leg = [f'<rect x="{lx-20}" y="{ly-70}" width="700" height="{110+len(unique_categories)*STEP}" fill="white"/>',
       f'<text x="{lx}" y="{ly+5}" font-weight="bold" font-size="51">Defense System</text>']
for i, c in enumerate(unique_categories):
    y = ly + 90 + i * STEP
    leg.append(f'<rect x="{lx}" y="{y-36}" width="42" height="42" fill="{category_colors[c]}"/>'
               f'<text x="{lx+68}" y="{y}" font-size="48">{escape(c)}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1300 -1300 3300 2600" width="3300" height="2600" font-family="Helvetica, Arial, sans-serif">
<rect x="-1300" y="-1300" width="3300" height="2600" fill="white"/>
<g stroke="black" stroke-width="2">{"".join(edges)}</g>
<g>{"".join(nodes)}</g>
<g font-size="{FS}" fill="black">{"".join(labels)}</g>
<g>{"".join(leg)}</g>
</svg>'''
open("panels/panelA_network.svg", "w").write(svg)
print("saved panels/panelA_network.svg")
