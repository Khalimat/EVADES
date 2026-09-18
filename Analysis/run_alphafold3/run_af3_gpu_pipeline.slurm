#!/bin/bash
# AlphaFold 3 stage 2 (GPU): structure inference from prepared input JSONs.
#
# WHAT IT DOES
#   SLURM array job: task N reads the N-th line of a text file listing JSON paths (typically
#   the *_data.json files written by run_af3_cpu_pipeline.slurm) and runs AlphaFold 3 on it inside
#   Singularity on one A100 GPU. The JSON's own folder is used for both input and output, so the
#   predicted models are written next to the JSON.
#
# ARGUMENT    $1 JSON_LIST_FILE   text file with one JSON path per line
# USAGE       Fill in the placeholder paths below, then
#               sbatch --array=0-(N-1) run_af3_gpu_pipeline.slurm json_list.txt
#             where N is the number of lines in json_list.txt.
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

# Site-specific paths, left as placeholders - fill in before running
MODEL_PARAMETERS_DIR=".."   # AF3 model weights
DB_DIR=".."                 # AF3 public databases
AF3_dir=".."                # AF3 source checkout containing run_alphafold.py
SIF_path=".."               # Singularity image with AF3

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
