#!/bin/bash
#SBATCH --job-name=alphafold3_array_cpu
#SBATCH --array=0-0                          # Placeholder, will be overridden
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=100G
#SBATCH --time=24:00:00
#SBATCH --output=logs/alphafold3-%A_%a.out
#SBATCH --error=logs/alphafold3-%A_%a.err

# Usage:
# sbatch --array=0-(N-1) test.slurm /path/to/input_dir /path/to/output_dir

# Load CUDA
module load cuda/12.6.3

# Parse arguments
INPUT_DIR=$1
OUTPUT_DIR=$2

# Define constants (I removed paths, as they are specific to my setup)
MODEL_PARAMETERS_DIR=".."
DB_DIR=".."
AF3_dir=".."
SIF_file=".."

# Get the list of .json files and pick one based on the SLURM task ID
JSON_FILES=($(ls ${INPUT_DIR}/*.json))
JSON_FILE="${JSON_FILES[$SLURM_ARRAY_TASK_ID]}"
JSON_FILENAME=$(basename "$JSON_FILE")
JSON_BASENAME="${JSON_FILENAME%.*}"
JOB_OUTPUT_DIR="${OUTPUT_DIR}/${JSON_BASENAME}"

# Create the per-job output directory if it doesn't exist
mkdir -p "${JOB_OUTPUT_DIR}"

echo "Running AlphaFold3 prep on ${JSON_FILENAME} (task ${SLURM_ARRAY_TASK_ID})"

singularity exec \
    --nv \
    --bind ${INPUT_DIR}:/root/af_input \
    --bind ${JOB_OUTPUT_DIR}:/root/af_output \
    --bind ${MODEL_PARAMETERS_DIR}:/root/models \
    --bind ${DB_DIR}:/root/public_databases \
    ${SIF_file} \
    python ${AF3_dir}/run_alphafold.py \
    --json_path=/root/af_input/${JSON_FILENAME} \
    --model_dir=/root/models \
    --db_dir=/root/public_databases \
    --output_dir=/root/af_output \
    --jackhmmer_n_cpu 8 \
    --run_inference=false

echo "Task ${SLURM_ARRAY_TASK_ID} completed"