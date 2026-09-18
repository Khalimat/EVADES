# Structure files — provenance

All three files were copied unchanged from the original Figure 3 working
directory and are the
exact coordinates behind the published figure. Nothing here was re-computed;
`scripts/01_render_panelA.py` and `02_render_panelB.py` only read them.

| file | = original | chains | what it is |
|------|-----------|--------|------------|
| `orf55_on_2q2u_FATCAT.pdb` | `2q2u.ORF55.pdb` | A = Chlorella-virus DNA ligase (2Q2U, static)<br>B = ORF55 (rigid-body "twisted" onto chain A) | FATCAT 2.0 rigid superposition. Header: *1 block, 287 residues, 2.001 Å RMSD*; P = 0.00e+00. Source of the residue pairs in **all of Panel B**. Re-verified on the public FATCAT server 2026-09-07 (287 positions / 2.00 Å / P = 0.00e+00): `../fatcat_inputs/FATCAT_web_result.md`. |
| `orf55_DNA_AF3.pdb` | `ORF55_DNA_complex.pdb` | A = ORF55 · B, C = 21-nt DNA strands | AlphaFold 3 model of ORF55 bound to the 21-bp duplex from 2Q2U (both strands modelled continuous / intact). Panel A row 2. |
| `2q2u_ligase_DNA.pdb` | `2q2u_DNA_complex.pdb` | A = DNA ligase · E, F = DNA (chain F has OMC = 2′-O-methyl-C at pos 9) · HOH | PDB **2Q2U**, Chlorella-virus DNA ligase–AMP bound to nicked/product duplex DNA (Nair et al. 2007, *Nat. Struct. Mol. Biol.* 14:770, https://www.nature.com/articles/nsmb1266; 3.0 Å). Waters are stripped at render time. Panel A row 3. |

## Reference frame

`orf55_on_2q2u_FATCAT.pdb` chain A and `2q2u_ligase_DNA.pdb` chain A are
byte-for-byte the same coordinates (raw 2Q2U crystal frame). The render script
brings the other two structures into that one frame:

* `2q2u_ligase_DNA.pdb`  → `align` chain A onto FATCAT chain A (ligase)
* `orf55_DNA_AF3.pdb`    → `align` chain A onto FATCAT chain B (ORF55)

So unlike the original figure (where each row was oriented by hand), the three
Panel-A rows here share a single coordinate frame and the four columns are then
exact 90° rotations of it about the screen x-axis.

## Active-site residue pairs (Panel B)

`data/active_site_residues.tsv` — 13 residues of the Chlorella-virus ligase
active site and the structurally equivalent ORF55 residue read off the FATCAT
superposition. Verified against the coordinates: 11/13 are identical, 2 are not —
**F75→C78** (Phe→Cys, flagged `-2`) and **K186→R186** (Lys→Arg, flagged `2`).
The `-2` / `2` are the **BLOSUM62 substitution scores** for those two changes
(F↔C = −2, non-conservative; K↔R = +2, conservative), reproducing the annotation
used in the original figure.
The `motif` and `role_nair2007` columns are transcribed from **Nair et al. 2007**
(*Nat. Struct. Mol. Biol.* 14:770): motif I = K27/D29/R32 (27-KIDGIR-32), motif Ia = R42
(41-SRTFKP-46), motif III = E67, motif IIIa = F98, motif IV = E161, motif V =
K186/K188, and the Arg285–Asp29 salt bridge locks the NTase–OB clamp. F75 is a
non-catalytic van-der-Waals contact to the 3′-terminal sugar.
