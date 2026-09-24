# Supplementary Figure 6 — AlphaFold 3 model confidence (pLDDT) and PAE

Self-contained copy of the code and data behind the supplementary figure showing, for every
structure prediction presented in the main figures, the model coloured by per-residue pLDDT and
its predicted aligned error (PAE) matrix, with ranking score / ipTM / pTM. Copied from
`../revision_17` (NTase runs from `../revision_4`). The figure title has been removed; the
page is 14 mm shorter so panel sizes are unchanged.

## Layout

```
├── run_all.sh                      regenerates everything in output/
├── output/
│   ├── Supplementary_Figure_pLDDT_PAE.{pdf,png,svg}   the figure (PNG at 300 dpi)
│   ├── Supplementary_Figure_6_caption.txt             figure legend
│   └── panels/                     per-target <name>_pLDDT.png, <name>_PAE.png, pLDDT_legend.png
├── scripts/
│   ├── targets.py                  the 8 models shown (panel order, labels, file paths)
│   ├── select_ntase_models.py      lists top-ranking_score NTase models (how those two were chosen)
│   ├── render_plddt.py             PyMOL cartoon + ligand sticks coloured by pLDDT (AlphaFold bins)
│   ├── render_pae.py               PAE heat maps with chain boundaries (matplotlib)
│   ├── make_legend.py              shared pLDDT colour key
│   ├── build_figure.py             assembles the 2 x 4 grid into the PDF (reportlab)
│   └── make_af3_jobs.py            builds inputs/af3_server_jobs/ from inputs/published_models/
├── inputs/
│   ├── published_models/           original model .cif files for the 6 Acr / Ocr complexes
│   │                               (source of the sequences; they carry no PAE)
│   └── af3_server_jobs/            AlphaFold Server job JSONs re-submitted (seed 1) to get PAE
└── af3_results/                    raw AlphaFold Server output, trimmed to what the scripts read
    ├── folds_2026_09_15_18_26/     6 re-runs (<target>_reseed_for_pae_seed1): model_0.cif,
    │                               full_data_0.json, summary_confidences_{0-4}.json, job_request.json
    └── ntase_utp_utp_mg/           NTase + UTP + UTP + 3 Mg, 5 seeds each for YP_009031408 and
                                    YP_009091875: summary_confidences + job_request for every seed;
                                    model .cif + full_data only for the model shown
```

Not copied: the other 4 samples' `.cif` / `full_data` JSONs, MSAs and templates (~360 MB), a
stale single-chain `NTase` render/job that was not used in the final figure, and the reviewer
comment that prompted this figure.

## Panels (model shown)

| panel | AF3 run | model | ranking | ipTM | pTM |
|---|---|---|---|---|---|
| AcrIC5–PaCas8c | acric5_reseed_for_pae_seed1 | 0 | 0.91 | 0.92 | 0.85 |
| AcrIC3–PaCas3 | acric3_reseed_for_pae_seed1 | 0 | 0.90 | 0.88 | 0.89 |
| AcrIB4–LsCas8b1 | acrib4_reseed_for_pae_seed1 | 0 | 0.88 | 0.91 | 0.75 |
| AcrIIA26–SpyCas9 | acriia26_reseed_for_pae_seed1 | 0 | 0.85 | 0.87 | 0.79 |
| NTase Bcp1 (YP_009031408)–UTP–UTP–Mg | ntase_yp_009031408_utp_utp_mg3_seed4 | 0 | 0.94 | 0.93 | 0.93 |
| NTase E. ello granulovirus (YP_009091875)–UTP–UTP–Mg | ntase_yp_009091875_utp_utp_mg3_seed2 | 1 | 0.95 | 0.93 | 0.88 |
| Ocr–DISARM DrmMII | disarm_ocr_complex_reseed_for_pae_seed1 | 0 | 0.75 | 0.72 | 0.87 |
| Ocr–Panchino gp28 | panchino_ocr_complex_reseed_for_pae_seed1 | 0 | 0.73 | 0.72 | 0.74 |

For the six re-runs, model 0 is AF Server's rank-1 model. For the NTases, a top-ranking model
across all 25 was used; AF Server rounds `ranking_score` to 2 decimals, so several models tie
(listed by `select_ntase_models.py`), all with near-identical ipTM/pTM.

pLDDT colours (protein and ligands): ≥ 90 `#0053D6`, 70–90 `#65CBF3`, 50–70 `#FFDB13`, < 50 `#FF7D45`.
PAE colour scale 0–31.75 Å (`Greens_r`).

## Reproduce

```
conda create -n suppfig -c conda-forge python=3.11 pymol-open-source numpy matplotlib reportlab poppler
conda activate suppfig
./run_all.sh
```

Changes from the original figure: title removed; all text 50 % larger; Mg2+ ions left out of the
NTase PAE plots (UTPs kept); ligands coloured by pLDDT
(were grey); atoms with pLDDT exactly 50/70/90 now coloured (were left uncoloured).
`make_af3_jobs.py` is not called by `run_all.sh`; it documents how the job JSONs were made.

AlphaFold Server output is subject to its terms of use (`af3_results/*/terms_of_use.md`).
