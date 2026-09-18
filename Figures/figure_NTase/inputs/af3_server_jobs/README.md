# AF3 server upload order

Jobs are split into two directories because AlphaFold Server's `ligand` entity only accepts a
small fixed CCD allowlist (`CCD_ADP`, `CCD_ATP`, `CCD_AMP`, `CCD_GTP`, `CCD_GDP`, `CCD_FAD`,
`CCD_NAD`, `CCD_NAP`, `CCD_NDP`, `CCD_HEM`, `CCD_HEC`, `CCD_PLM`, `CCD_OLA`, `CCD_MYR`,
`CCD_CIT`, `CCD_CLA`, `CCD_CHL`, `CCD_BCL`, `CCD_BCB` —
[source](https://github.com/google-deepmind/alphafold/blob/main/server/README.md)). CTP and
UTP are not on it, which is the "unknown ligand" error.

## 1. `no_utp_ctp/` — upload this now, no caveats

30 jobs (ATP-ATP, ATP-GTP, GTP-GTP pairs x 2 proteins x 5 seeds), using the documented,
confirmed-working `"ligand": {"ligand": "CCD_ATP", "count": 1}` schema (same schema as the earlier ATP/GTP/UTP experiment).
Upload `af3_server_batch_1.json` directly.

## 2. `with_utp_ctp/` — schema confirmed; expect partial-batch failures, retry as needed

70 jobs (every pair including CTP and/or UTP), split into 3 batches of ≤30
(`af3_server_batch_1.json`: 30, `batch_2.json`: 30, `batch_3.json`: 10).

Ligand schema history for CTP/UTP (all attempts used the same `"ligand"` sequence-entry type
as ATP/GTP — only the inner value changed):
1. `"ligand": {"ligand": "CCD_CTP", "count": 1}` → server error **"unknown ligand"** (CTP/UTP
   aren't in the server's small CCD allowlist — confirmed from the public schema docs).
2. `"ligand": {"ccdCodes": ["CTP"], "count": 1}` → server error **"ligand is undefined"** (the
   parser still needs a `"ligand"` string key, not `"ccdCodes"`).
3. `"ligand": {"ligand": "CTP", "count": 1}` (raw code, no `CCD_` prefix) — **CONFIRMED WORKING**:
   verified 2026-09-09 against `af3_results/with_utp_ctp/af3_server_batch_1_partial/*/`
   `*_job_request.json`, which is the server's own echo of what it parsed and ran successfully.
   This is what `generate_af3_jobs.py` now writes for every CTP/UTP ligand entry.

**Batch launches can still partially fail even with a correct schema.** Uploading
`af3_server_batch_1.json` (30 jobs, all schema-3 above) got only 15/30 to actually launch as
trackable jobs — the other 15 silently consumed quota with no job history entry at all (see
`af3_results/with_utp_ctp/af3_server_batch_1_partial/` for the 15 that did complete). This
looks like a transient/rate-limit issue on the server's batch-launch path, not a payload
problem — failures weren't tied to a specific NTP pair (e.g. all 5 CTP-CTP and all 5 CTP-UTP
seeds launched fine, 0/5 ATP-CTP did). `af3_server_batch_1_retry.json` in this directory holds
just the 15 jobs that didn't launch, ready to re-upload. If retrying still drops jobs, prefer
smaller sub-batches (e.g. 10 at a time) over one 30-job upload.
