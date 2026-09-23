# Supplementary Figure 2 — ORF55 + ATP with nicked / 1-nt-gap / 2-nt-gap DNA

Clean copy of the code and data behind the figure.

- `renders/SuppFig_ORF55_DNA_structures.png` — final figure (A interface, B pLDDT); `SuppFig_structures_caption.txt` — caption
- `renders/parts/` — per-substrate PyMOL panels; `SuppFig_interface_overview.png` / `SuppFig_plddt.png` — rows A / B alone
- `models/` — highest-ranked AF3 model per seed and overall best (`*_best.cif`) per substrate, including `intact_*.cif` (restored from `revision_2/pymol/models/`, byte-identical — needed for the interface table below, not used in the montage); `manifest.tsv` = provenance
- `af3_results/` — AlphaFold Server output (models + confidence JSONs; MSAs, templates and full_data JSONs omitted for size) for nicked, gap1nt, gap2nt and intact duplex (intact is only used for the pLDDT comparison and the interface table), 5 seeds x 5 models
- `inputs/` — AF3 job JSONs, original `ORF55.cif`, sequences
- `supplementary/` — `AF3_interface_quant.tsv` (Supplementary Table, interface quantification) + `AF3_interface_quant_table_legend.txt`
- `scripts/` — paths are relative to this folder

Chains: A = ORF55, B = ATP, C = continuous strand, D = upstream arm (3'-OH), E = downstream arm (5'-P).

## Reproduce
```
/Applications/PyMOL.app/Contents/bin/pymol -cq scripts/pymol_render.py     # -> renders/parts/*.png
python3 scripts/montage_pymol.py                                          # -> renders/SuppFig_*.png + caption
python3 scripts/plddt_quant.py                                            # DNA/protein pLDDT + permutation test quoted in caption
/Applications/PyMOL.app/Contents/bin/pymol -cq scripts/interface_quant.py  # -> supplementary/AF3_interface_quant.tsv (Supplementary Table)
```
