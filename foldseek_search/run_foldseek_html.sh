#!/usr/bin/env bash
#SBATCH --job-name=foldseek-easy
#SBATCH --output=%x_%A_%a.out
#SBATCH --error=%x_%A_%a.err
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=10
# Memory must be provided at submission time, e.g.:
#   sbatch --mem=64G --array=0-267 foldseek_easy_search_array.slurm <DB_PATH> <OUT_DIR_NAME>

set -euo pipefail

# === Positional arguments ===
DB_PATH="${1:-}"
OUT_NAME="${2:-}"

# === Fixed paths === (I removed paths, as they are specific to my setup)
QUERY_DIR=".."
RESULTS_BASE=".."

# === Validate inputs ===
if [[ -z "${DB_PATH}" || -z "${OUT_NAME}" ]]; then
  echo "Usage: sbatch [--mem=XXG] --array=0-(N-1) $0 /path/to/foldseek_db <output_dir_name>"
  exit 1
fi
[[ -d "${QUERY_DIR}" ]] || { echo "ERROR: Query directory not found: ${QUERY_DIR}"; exit 1; }
[[ -e "${DB_PATH}"  ]] || { echo "ERROR: Database path not found: ${DB_PATH}"; exit 1; }

# === Collect CIFs deterministically ===
shopt -s nullglob
mapfile -d '' CIFS < <(find "${QUERY_DIR}" -maxdepth 1 -type f -name '*.cif' -print0 | sort -z)
NUM=${#CIFS[@]}
if [[ "${NUM}" -eq 0 ]]; then
  echo "ERROR: No .cif files found in ${QUERY_DIR}"
  exit 1
fi

# === Bounds check for array index ===
TASK_ID="${SLURM_ARRAY_TASK_ID:-}"
if [[ -z "${TASK_ID}" ]]; then
  echo "ERROR: SLURM_ARRAY_TASK_ID is not set. Submit with --array=0-$((NUM-1))"
  exit 1
fi
if (( TASK_ID < 0 || TASK_ID >= NUM )); then
  echo "ERROR: SLURM_ARRAY_TASK_ID ${TASK_ID} out of range [0, $((NUM-1))]"
  exit 1
fi

QUERY="${CIFS[${TASK_ID}]}"
MODEL_NAME="$(basename "${QUERY}" .cif)"

OUT_DIR="${RESULTS_BASE}/${OUT_NAME}"
mkdir -p "${OUT_DIR}"
OUT_M8="${OUT_DIR}/${MODEL_NAME}.m8"
OUT_HTML="${OUT_DIR}/${MODEL_NAME}.html"

# Load Foldseek (adjust to your environment if needed)
module load foldseek/8-ef4e960 2>/dev/null || echo "Warning: ensure Foldseek is available in your PATH"

echo "=== Foldseek easy-search (task ${TASK_ID}/${NUM}) ==="
echo "Model:    ${MODEL_NAME}"
echo "Query:    ${QUERY}"
echo "Database: ${DB_PATH}"
echo "Results:  ${OUT_M8} , ${OUT_HTML}"
echo "Threads:  10"
echo "---------------------------------------"

# Optional: help native threading behave
export OMP_NUM_THREADS=10

foldseek easy-search \
  "${QUERY}" \
  "${DB_PATH}" \
  "${OUT_M8}" \
  "${OUT_HTML}" \
  -e 0.00001 \
  --threads 10 \
  --format-mode 3

echo "Done: ${MODEL_NAME}"

