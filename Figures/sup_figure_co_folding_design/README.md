# Supplementary Figure X — design of the ADP–defence protein co-folding screen

Schematic (no plotted data): (a) each ADP co-folded with every protein of the defence system it inhibits;
(b) 433 pairs x 20 models (5 models x 4 seeds) = 8,660 structures, filtered at mean ipTM >= 0.6.

- `SuppFig_cofolding_screen.{svg,pdf,png}` — final figure
- `make_figure.py` — hand-drawn SVG generator (writes next to itself; PDF/PNG need `cairosvg`, which needs the system cairo library). The SVG regenerates byte-identical to the shipped one.
- `data/co_folding_uncharacterised_adps_defence_average_scores.csv` — per-pair scores behind the numbers in the schematic:
  433 pairs, n_samples = 20 each (-> 8,660), 93 ADPs, 166 defence proteins, 22 pairs with mean ipTM >= 0.6.
  The `path` column is `<analysis dir>/<defence-protein accession>/<ADP>/<pair>`, relative to the analysis output root.

Not derivable from the CSV: the count of 19 defence systems and the per-system protein counts (13 / 6 / 2 for type I-A CRISPR–Cas, BREX type I, Gabija) — these are hardcoded in `make_figure.py`.
