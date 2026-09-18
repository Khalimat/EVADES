#!/usr/bin/env bash
# Search viral/phage protein databases for homologs of a query protein set (BLASTP).
#
# WHAT IT DOES
#   For each database listed in DBS below (GenBank phage, GenBank viral, IMG/VR):
#     1. runs BLASTP of QUERY against it (E-value <= EVALUE, up to 500 hits per query);
#     2. writes all hits to <OUT_BASE>/<db>/blast_raw.tsv;
#     3. keeps hits with >= 30 % identity and >= 80 % query coverage
#        -> <OUT_BASE>/<db>/blast_filtered.tsv.
#
# INPUT   QUERY    protein FASTA of the queries (set below)
#         DBS      prefixes of pre-built BLAST protein databases (makeblastdb -dbtype prot)
# OUTPUT  OUT_BASE/<db>/blast_raw.tsv and blast_filtered.tsv
#         columns: qseqid sseqid evalue pident qlen slen qstart qend sstart send
#
# USAGE   Fill in QUERY, OUT_BASE and the DBS prefixes, then:  sbatch adp_homologs_all.sh
#         (needs BLAST+ on the PATH; add `module load blast+` if your cluster uses modules).
#         Downstream: add_sequences.py and add_genome_id.py annotate the filtered hits.
#SBATCH --job-name=adp_homologs
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=%x-%j.out

# Paths are site-specific and left as placeholders: fill them in before running.
QUERY=".."       # query protein FASTA
OUT_BASE=".."    # output directory (one sub-folder per database)
EVALUE="1e-5"      # BLASTP E-value cutoff

# Optional: load BLAST+ on your cluster
# module load blast+ 2>/dev/null || true

set -euo pipefail
THREADS=${SLURM_CPUS_PER_TASK:-1}
OUTFMT="6 qseqid sseqid evalue pident qlen slen qstart qend sstart send"

# Label -> BLAST database prefix (site-specific placeholders; fill in before running)
declare -A DBS=(
  ["GenBank_phage"]=".."
  ["GenBank_viral"]=".."
  ["IMG_VR"]=".."
)

# tiny helper: minimally verify DB looks OK (either .pal alias or .pin exists)
check_db () {
  local pref="$1"
  if [[ -s "${pref}.pal" || -s "${pref}.pin" || $(compgen -G "${pref}".[0-9][0-9].pin | head -n1) ]]; then
    return 0
  else
    echo "ERROR: ${pref} doesn't look like a BLAST protein DB (no .pal/.pin found)" >&2
    return 1
  fi
}

echo "[INFO] Using $THREADS threads; E-value ${EVALUE}"
echo "[INFO] Query: $QUERY"
echo "[INFO] Output base: $OUT_BASE"
echo

for label in "${!DBS[@]}"; do
  prefix="${DBS[$label]}"
  outdir="${OUT_BASE}/${label}"
  mkdir -p "$outdir"

  raw="${outdir}/blast_raw.tsv"
  filt="${outdir}/blast_filtered.tsv"

  echo "[${label}] Checking DB: $prefix"
  check_db "$prefix"

  echo "[${label}] Running BLASTP -> $raw"
  # header
  printf "qseqid\tsseqid\tevalue\tpident\tqlen\tslen\tqstart\tqend\tsstart\tsend\n" > "$raw"

  blastp \
    -query "$QUERY" \
    -db "$prefix" \
    -outfmt "$OUTFMT" \
    -evalue "$EVALUE" \
    -max_target_seqs 500 \
    -num_threads "$THREADS" >> "$raw"

  echo "[${label}] Filtering (>=30%% id and >=80%% query coverage) -> $filt"
  # columns: 1 qseqid 2 sseqid 3 evalue 4 pident 5 qlen 6 slen 7 qstart 8 qend 9 sstart 10 send
  awk -F'\t' 'NR==1 || (NR>1 && $4>=30 && (($8-$7+1)/$5)>=0.80)' "$raw" > "$filt"

  # quick summary
  nraw=$(($(wc -l < "$raw")-1))
  nfilt=$(($(wc -l < "$filt")-1))
  echo "[${label}] Done: ${nraw} hits raw; ${nfilt} hits after filtering."
  echo
done

echo "[ALL DONE] Results are under: $OUT_BASE"
