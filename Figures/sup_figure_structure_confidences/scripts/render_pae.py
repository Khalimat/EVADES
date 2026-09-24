"""PAE heat map (rank-1 / selected model) per target, chain boundaries marked.
Ion chains (e.g. the 3 Mg2+ in the NTase runs) are left out of the matrix."""
import glob, os, json, string
from targets import TARGETS, RENDERS

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs(RENDERS, exist_ok=True)


def ion_chains(full_data_path):
    """Chain IDs of ions, from the job request next to full_data (AF Server letters chains A, B, ...
    in job order, one per copy)."""
    job = json.load(open(glob.glob(os.path.join(os.path.dirname(full_data_path), "*_job_request.json"))[0]))[0]
    letters, ions = iter(string.ascii_uppercase), set()
    for entry in job["sequences"]:
        (kind, spec), = entry.items()
        for _ in range(int(spec.get("count", 1))):
            chain = next(letters)
            if kind == "ion":
                ions.add(chain)
    return ions


for t in TARGETS:
    with open(t["full_data"]) as f:
        d = json.load(f)
    drop = ion_chains(t["full_data"])
    keep = [i for i, c in enumerate(d["token_chain_ids"]) if c not in drop]
    pae = np.array(d["pae"])[np.ix_(keep, keep)]
    chain_ids = [d["token_chain_ids"][i] for i in keep]
    if drop:
        print(f"{t['name']}: dropped ion chains {sorted(drop)} from PAE")

    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    im = ax.imshow(pae, cmap="Greens_r", vmin=0, vmax=31.75, origin="upper")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=15)
    cbar.set_label("Predicted aligned error (Å)", fontsize=13.5)

    # chain boundary lines
    chains = []
    prev = None
    for i, c in enumerate(chain_ids):
        if c != prev:
            chains.append(i)
            prev = c
    for b in chains[1:]:
        ax.axhline(b - 0.5, color="black", linewidth=0.6)
        ax.axvline(b - 0.5, color="black", linewidth=0.6)

    # chain labels at midpoints
    unique_chains = []
    prev = None
    start = 0
    bounds = []
    for i, c in enumerate(chain_ids):
        if c != prev:
            if prev is not None:
                bounds.append((prev, start, i))
            prev = c
            start = i
    bounds.append((prev, start, len(chain_ids)))
    ticks = [ (s+e)/2 for (_, s, e) in bounds ]
    labels = [ c for (c, _, _) in bounds ]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=13.5)
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=13.5)
    ax.tick_params(labelsize=13.5)
    ax.set_xlabel("Scored residue (chain)", fontsize=13.5)
    ax.set_ylabel("Aligned residue (chain)", fontsize=13.5)
    ax.set_title("PAE (rank 1 model)", fontsize=15)

    fig.tight_layout()
    out_png = os.path.join(RENDERS, f"{t['name']}_PAE.png")
    fig.savefig(out_png, dpi=300)
    plt.close(fig)
    print(f"rendered {out_png}")

print("done")
