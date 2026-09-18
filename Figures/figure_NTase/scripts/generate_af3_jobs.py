#!/usr/bin/env python3
"""Generate AlphaFold 3 server batch-upload JSONs for the NTase + NTP-pair + Mg2+ co-folding experiment.

WHAT IT DOES
    Builds the job files uploaded to the AlphaFold Server to co-fold each of two
    nucleotidyltransferases (NTases) with every unordered pair of NTPs and three
    Mg2+ ions, using 5 independent seeds per condition. Five seeds (each server job
    yields 5 diffusion samples, i.e. 25 models per condition) let ipTM/pTM be
    reported as mean +/- SD and compared statistically between substrate pairs
    (analysed in make_supp_figure.py).

CONDITIONS
    Proteins : Bacillus phage Bcp1 NTase (YP_009031408.1) and its homolog from
               Erinnyis ello granulovirus (YP_009091875.1).
    Ligands  : every unordered pair from {ATP, GTP, CTP, UTP} (10 pairs) + 3 Mg2+.
    CTP is included alongside ATP/GTP/UTP because CD-NTases (the enzyme family
    under study; Govande et al 2021, Whiteley et al 2019) can use all four
    canonical NTPs and produce cytidine-containing cyclic nucleotides
    (e.g. c-CMP-UMP, c-di-UMP), so all four are tested.

LIGAND SCHEMA SPLIT (details in inputs/af3_server_jobs/README.md)
    AlphaFold Server's documented `ligand` entity only allows a small fixed CCD
    list (CCD_ATP, CCD_GTP, CCD_ADP, ... - NOT CCD_CTP or CCD_UTP; see
    https://github.com/google-deepmind/alphafold/blob/main/server/README.md);
    CCD_CTP / CCD_UTP give "unknown ligand". The web UI has a separate "CCD Code"
    entity that resolves arbitrary PDB codes, and its batch-upload key is the same
    "ligand" key with the raw, unprefixed code: `"ligand": {"ligand": "UTP", "count": N}`.
    This was confirmed (2026-09-09) from a completed job's own echoed
    `*_job_request.json`. Two earlier attempts failed: "unknown ligand" for
    CCD_CTP and "ligand is undefined" for a ccdCodes-list variant.

OUTPUT (under inputs/af3_server_jobs/)
    no_utp_ctp/    3 NTP pairs (AA, AG, GG) x 2 proteins x 5 seeds = 30 jobs, using the
                   `"ligand": {"ligand": "CCD_ATP"}` restricted-list schema.
    with_utp_ctp/  7 NTP pairs (AC, AU, GC, GU, CC, CU, UU) x 2 proteins x 5 seeds = 70 jobs,
                   using the `"ligand": {"ligand": "UTP"}` (unprefixed) schema.
    Each directory gets one JSON per (protein, NTP-pair), an all-jobs bundle, and
    <=30-job batch files. Even with a correct schema, AF3 server batch launches can
    silently drop some jobs (no job-history entry, quota still spent); see
    af3_server_batch_1_retry.json and inputs/af3_server_jobs/README.md for how that
    was recovered.

USAGE
    python3 scripts/generate_af3_jobs.py
    Re-running regenerates with_utp_ctp/af3_server_batch_*.json and
    af3_server_all_jobs.json from scratch but does not touch hand-made retry files.
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "inputs", "af3_server_jobs")

PROTEINS = {
    "YP_009031408": (
        "MKTVDLSVTGMSWMEERTILLTPYGSRLYGTDTENSDWDFKGVCIPPKEYFLGLETFNEYNNTGGKTFKN"
        "TKDDVDINIIHVSKFVKDAMHGVPNNIEVLFAREQDYIILTELGQVLRDNRHLFLSKQIITKFGGYTRSL"
        "TNKLKNGAGRQELVEEFGYDTKNFMQGVRLQLSAIEILETGDYSTYRPERDFLLGCRNGEYTREQALALV"
        "ESYDERLQVAHENSKLPEKPDYNKINGMLMAINEDALKFGIHS"
    ),
    "YP_009091875": (
        "MVYIVIDTGSRAKGYAVESSDFDFKVYTKCSREQFELYIQDKQILKNTHKRVELCNVIKTETSHQLCDVV"
        "YIDLYVGMIGIVTGKNPELGVFVKEHDVKNEEDDTVNTPLYEFIKQLTHLSMCAITTTMMKYAILRTNKN"
        "LLQLMFNYVYVEYYLKHGKAPSSTRILDIVHEMNDTPETLYVDMYAKLMKRETCDAQDVIFFEQWKSDIL"
        "QRLKCTCNAHQQAVLRHNVVMYALNLQKSEIKPCVCCVNNYIFPKYNTN"
    ),
}

# NTPs that the server's documented ligand allowlist accepts as CCD_<name> (not CTP/UTP).
SERVER_ALLOWED_NTPS = {"ATP", "GTP"}

# All 4 canonical NTPs -> every unordered pair incl. homo-pairs (AA, AG, ..., UU) = 10 pairs,
# split by which ligand schema the server needs.
NTPS = ["ATP", "GTP", "CTP", "UTP"]
NTP_PAIRS = [(a, b) for i, a in enumerate(NTPS) for b in NTPS[i:]]
NO_UTP_CTP_PAIRS = [(a, b) for a, b in NTP_PAIRS if a in SERVER_ALLOWED_NTPS and b in SERVER_ALLOWED_NTPS]
WITH_UTP_CTP_PAIRS = [p for p in NTP_PAIRS if p not in NO_UTP_CTP_PAIRS]

N_SEEDS = 5     # independent seeds per condition
N_MG = 3        # Mg2+ ions per job
BATCH = 30       # max jobs per uploaded batch file (server daily quota / batch size)


def ntp_ligand_entry(ntp):
    """Return the AF3-server `sequences` entry for one NTP, using whichever ligand schema the server accepts for it."""
    if ntp in SERVER_ALLOWED_NTPS:
        return {"ligand": {"ligand": f"CCD_{ntp}", "count": 1}}
    # Confirmed schema for CTP/UTP (see module docstring): same "ligand" key as the restricted
    # list, but the raw unprefixed CCD code - matching the "CCD Code" UI entity, which takes a
    # plain code like "UTP", not "CCD_UTP". Verified from a completed job's own job_request.json.
    return {"ligand": {"ligand": ntp, "count": 1}}


def make_job(protein_id, seq, ntp_a, ntp_b, seed):
    """One AF3 server job: protein x1, two NTP ligands, 3 Mg2+, a single model seed."""
    return {
        "name": f"NTase_{protein_id}_{ntp_a}_{ntp_b}_Mg3_seed{seed}",
        "modelSeeds": [seed],
        "sequences": [
            {"proteinChain": {"sequence": seq, "count": 1}},
            ntp_ligand_entry(ntp_a),
            ntp_ligand_entry(ntp_b),
            {"ion": {"ion": "MG", "count": N_MG}},
        ],
    }


def write_batch_set(subdir, pairs):
    """Write per-condition files, an all-jobs bundle and <=BATCH-job batch files into
    inputs/af3_server_jobs/<subdir>; return the list of all jobs."""
    out = os.path.join(OUT, subdir)
    os.makedirs(out, exist_ok=True)
    all_jobs = []
    for protein_id, seq in PROTEINS.items():
        for ntp_a, ntp_b in pairs:
            jobs = [make_job(protein_id, seq, ntp_a, ntp_b, seed) for seed in range(1, N_SEEDS + 1)]
            fname = f"af3_{protein_id}_{ntp_a}_{ntp_b}_5seeds.json"
            with open(os.path.join(out, fname), "w") as fh:
                json.dump(jobs, fh, indent=2)
            all_jobs.extend(jobs)
    with open(os.path.join(out, "af3_server_all_jobs.json"), "w") as fh:
        json.dump(all_jobs, fh, indent=2)
    for i in range(0, len(all_jobs), BATCH):
        n = i // BATCH + 1
        with open(os.path.join(out, f"af3_server_batch_{n}.json"), "w") as fh:
            json.dump(all_jobs[i:i + BATCH], fh, indent=2)
    return all_jobs


no_jobs = write_batch_set("no_utp_ctp", NO_UTP_CTP_PAIRS)
with_jobs = write_batch_set("with_utp_ctp", WITH_UTP_CTP_PAIRS)

# One-job smoke-test file: sanity-check a fresh account/quota before spending a full
# batch, since batch launches can partially fail (see af3_server_batch_1_retry.json and
# inputs/af3_server_jobs/README.md).
verify_dir = os.path.join(OUT, "with_utp_ctp")
with open(os.path.join(verify_dir, "VERIFY_FIRST.json"), "w") as fh:
    json.dump([with_jobs[0]], fh, indent=2)

print(f"no_utp_ctp/:   {len(NO_UTP_CTP_PAIRS)} NTP pairs x {len(PROTEINS)} proteins x {N_SEEDS} seeds "
      f"= {len(no_jobs)} jobs (confirmed-working CCD_ATP/CCD_GTP ligand schema)")
print(f"with_utp_ctp/: {len(WITH_UTP_CTP_PAIRS)} NTP pairs x {len(PROTEINS)} proteins x {N_SEEDS} seeds "
      f"= {len(with_jobs)} jobs (confirmed-working unprefixed-ligand schema)")
print("\nNote: rerunning this script regenerates with_utp_ctp/af3_server_batch_*.json and "
      "af3_server_all_jobs.json from scratch, but does NOT touch af3_server_batch_1_retry.json "
      "or any other hand-made retry file (different filename) - safe to rerun after edits.")
