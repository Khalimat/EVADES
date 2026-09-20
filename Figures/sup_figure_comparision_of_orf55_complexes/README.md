# Supplementary figure — comparison of predicted ORF55 + ATP complexes with three DNA substrates

Self-contained code and data for the figure comparing AlphaFold 3 models of ORF55 + ATP bound to a
21-bp DNA duplex that is **nicked**, has a **1-nt gap**, or has a **2-nt gap**
(A: enzyme–DNA interface; B: same models coloured by pLDDT). Copied from `../revision_2`
(was "Fig 2" there).

## Reproduce

```
./run_all.sh          # ~1 min; needs python3 (numpy, pillow) and PyMOL (PYMOL=/path/to/pymol to override)
```

| step | script | in → out |
|---|---|---|
| 1 | `scripts/01_select_models.py` | `inputs/selected_models.tsv` + `af3_results/` → `models/*.cif` |
| 2 | `scripts/02_pymol_render.py` (PyMOL) | `models/*_best.cif` → `output/parts/{A,B}_<substrate>.png` |
| 3 | `scripts/03_montage.py` | parts → `output/SuppFig_*.png`, `output/SuppFig_structures_caption.txt` |
| 4 | `scripts/04_plddt_quant.py` | all 100 raw models → `output/plddt_stats.txt` (numbers quoted in the caption) |

## Layout

```
├── run_all.sh · requirements.txt
├── scripts/                 01–04 as above (paths are relative to the project root)
├── inputs/
│   ├── af3_server_jobs/     AlphaFold Server input JSONs (5 seeds per substrate) + ORF55_DNA.fasta
│   └── selected_models.tsv  which raw model was used per substrate x seed; best_overall=1 marks the one drawn
├── af3_results/folds_2026_09_03_19_12/   raw AF3 Server output, trimmed to model CIFs, summary
│                            confidences and job requests (4 substrates x 5 seeds x 5 samples)
├── models/                  derived by step 1: <substrate>_seed<N>.cif and <substrate>_best.cif
└── output/
    ├── SuppFig_ORF55_DNA_structures.png     the figure (A + B)
    ├── SuppFig_interface_overview.png       row A alone
    ├── SuppFig_plddt.png                    row B alone
    ├── SuppFig_structures_caption.txt       legend
    ├── plddt_stats.txt                      per-model / per-seed pLDDT and permutation tests
    └── parts/                               individual panels
```

Substrate keys: `nicked`, `gap1nt`, `gap2nt`, and `intact` (intact duplex control, used only for the
pLDDT statistics, not drawn). Chains: A = ORF55, B = ATP, C = continuous strand, D = upstream arm
(3'-OH), E = downstream arm (5'-P).

## Notes

- **Model selection is recorded, not recomputed.** The server summary JSONs store ranking scores
  rounded to 2 decimals, so ties between samples cannot be re-broken from the shipped files (I tried
  several tie-break rules; none reproduced the original picks). `selected_models.tsv` is the
  authoritative record; the copied `.cif` files are byte-identical to the originals in
  `revision_2/pymol/models/`.
- **Reproducibility check.** Regenerated caption is byte-identical to the original and the
  pLDDT statistics match it (DNA pLDDT 2-nt gap 81.9 ± 5.0 vs 95–96.5; P = 0.008). Re-rendered PNGs
  are the same size and differ from the originals only by ray-tracing noise (max 23/255 per channel,
  no pixel differing by more than 30 summed over RGB).
- Not included: Supplementary Table S1 (`interface_quant.py`), the ipTM/pTM figure (see
  `../sup_figure_af3_confidences_ORF55_DNA`), MSAs/templates/full_data JSONs, and the accidental
  `intact_duplex_atp_seed{2,3}_2` re-runs.
- Legal: `af3_results/.../terms_of_use.md` applies to the AF3 outputs.
