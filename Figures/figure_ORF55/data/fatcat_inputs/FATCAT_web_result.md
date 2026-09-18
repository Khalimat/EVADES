# FATCAT pairwise alignment — web-server reproduction

Re-run of the ORF55 vs Chlorella-virus DNA ligase structural alignment on the
FATCAT pairwise server (https://fatcat.godziklab.org/fatcat/fatcat_pair.html),
to independently confirm the numbers quoted in Figure 3 / the manuscript.

## Inputs (both uploaded as files)

| slot | file | contents | residues |
|------|------|----------|----------|
| pdb1 | `2q2u_A.pdb` | Chlorella-virus DNA ligase, chain A of PDB 2Q2U (protein only, waters/DNA stripped) | 293 |
| pdb2 | `orf55.pdb`  | ORF55 (phage DruSM1), chain A of the AlphaFold 3 model (protein only) | 304 |

Alignment mode: **rigid** (FATCAT forced to rigid comparison).

Both files were generated from `data/structures/orf55_DNA_AF3.pdb` and
`data/structures/2q2u_ligase_DNA.pdb`.

## Result  (job id `result_1788786430.2169213`, run 2026-09-07)

```
Align pdb1.pdb 293 with pdb2.pdb 304
Twists 0  ini-len 240  ini-rmsd 1.33  opt-equ 287  opt-rmsd 2.00  chain-rmsd 1.33
Score 661.89  align-len 301  gaps 14 (4.65%)
P-value 0.00e+00  Afp-num 28864  Identity 27.57%  Similarity 46.84%
Block 0  afp 30  score 661.89  rmsd 1.33  gap 53
```

Server summary text:
> These two structures are significantly similar with P-value of 0.00e+00
> (raw FATCAT score is 661.89). They have **287 equivalent positions with an
> RMSD of 2.00 Å without twists**.

## Reproduces the original exactly

| quantity | original figure / `orf55_on_2q2u_FATCAT.pdb` header | web re-run |
|---|---|---|
| blocks / twists | 1 block | 0 twists (= 1 rigid block) |
| equivalent positions | 287 | 287 |
| RMSD | 2.001 Å | 2.00 Å |
| P-value | 0.00e+00 | 0.00e+00 |
| sequence identity over the alignment | (not reported) | 27.6 % |

So the "FATCAT 2.0, 1 block, 287 aligned residues, 2.0 Å RMSD, P = 0.00 × 10⁰"
statement in the Figure 3 legend is confirmed by re-running the public
server. (The separate "1.2 Å Cα RMSD" figure in the latch text is from PyMOL
`align` over the trimmed core, not FATCAT — that distinction is kept in the
caption.)
