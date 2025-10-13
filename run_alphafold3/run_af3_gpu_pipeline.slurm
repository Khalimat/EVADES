#!/bin/bash
#SBATCH --job-name=alphafold3_array_gpu
#SBATCH --array=0-0             # Will be overridden when submitting
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=80G
#SBATCH --time=24:00:00
#SBATCH --output=logs/alphafold3-%A_%a.out
#SBATCH --error=logs/alphafold3-%A_%a.err

# Load CUDA
module load cuda/12.6.3

# Parse arguments
JSON_LIST_FILE=$1  # Path to a file listing .json paths

# Get JSON file for this SLURM array task
JSON_FILE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$JSON_LIST_FILE")
JSON_FILENAME=$(basename "$JSON_FILE")
JSON_BASENAME="${JSON_FILENAME%.*}"
JOB_OUTPUT_DIR=$(dirname "$JSON_FILE")
INPUT_DIR=$(dirname "$JSON_FILE")
RELATIVE_PATH=$(realpath --relative-to="${INPUT_DIR}" "${JSON_FILE}")

# Directories (I removed paths, as they are specific to my setup)
MODEL_PARAMETERS_DIR=".."
DB_DIR=".."
AF3_dir=".."
SIF_path=".."

echo "Running AlphaFold3 on ${JSON_FILENAME} (task ${SLURM_ARRAY_TASK_ID})"

singularity exec \
  --nv \
  --bind ${INPUT_DIR}:/root/af_input \
  --bind ${JOB_OUTPUT_DIR}:/root/af_output \
  --bind ${MODEL_PARAMETERS_DIR}:/root/models \
  --bind ${DB_DIR}:/root/public_databases \
  ${SIF_path} \
  python ${AF3_dir}/run_alphafold.py \
  --json_path=/root/af_input/${RELATIVE_PATH} \
  --model_dir=/root/models \
  --db_dir=/root/public_databases \
  --output_dir=/root/af_output

echo "Task ${SLURM_ARRAY_TASK_ID} completed"
